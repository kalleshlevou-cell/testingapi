"""Unit tests for the AI Link Analysis API."""

import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.config import get_settings, Settings
from app.utils.validators import validate_url, URLValidationError
from app.services.website_extractor import WebsiteContent


# Override settings for tests so GOOGLE_API_KEY is not required
def _test_settings() -> Settings:
    return Settings(google_api_key="test-key-not-real", llm_model="gemini-2.5-flash")


app.dependency_overrides[get_settings] = _test_settings

client = TestClient(app)


# ── Health Check ─────────────────────────────────────────────────────────────
class TestHealthCheck:
    def test_health_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


# ── URL Validation ───────────────────────────────────────────────────────────
class TestURLValidation:
    def test_empty_url(self):
        with pytest.raises(URLValidationError, match="empty"):
            validate_url("")

    def test_invalid_scheme(self):
        with pytest.raises(URLValidationError, match="Unsupported URL scheme"):
            validate_url("ftp://example.com")

    def test_localhost_blocked(self):
        with pytest.raises(URLValidationError, match="not allowed"):
            validate_url("http://localhost/admin")

    def test_private_ip_blocked(self):
        with pytest.raises(URLValidationError, match="not allowed"):
            validate_url("http://192.168.1.1")

    def test_valid_url(self):
        result = validate_url("https://www.google.com")
        assert result == "https://www.google.com"


# ── API Input Validation ────────────────────────────────────────────────────
class TestAPIInputValidation:
    def test_missing_url(self):
        response = client.post("/link-analysis", json={})
        assert response.status_code == 422

    def test_invalid_url_format(self):
        response = client.post("/link-analysis", json={"url": "not-a-url"})
        assert response.status_code == 422


# ── WebsiteContent ───────────────────────────────────────────────────────────
class TestWebsiteContent:
    def test_to_prompt_text(self):
        content = WebsiteContent(
            url="https://example.com",
            title="Example",
            meta_description="An example site",
            headings=["Welcome", "About Us"],
            paragraphs=["We are a technology company."],
        )
        text = content.to_prompt_text()
        assert "https://example.com" in text
        assert "Example" in text
        assert "technology company" in text

    def test_to_prompt_text_truncation(self):
        content = WebsiteContent(
            url="https://example.com",
            paragraphs=["A" * 100] * 1000,
        )
        text = content.to_prompt_text(max_chars=500)
        assert len(text) <= 530  # 500 + truncation message


# ── Full Pipeline (Mocked) ──────────────────────────────────────────────────
class TestLinkAnalysisPipeline:
    @patch("app.services.analysis_service.analyse_with_llm")
    @patch("app.services.analysis_service.extract_website_content")
    @patch("app.main.validate_url", return_value="https://example.com")
    def test_successful_analysis(self, mock_validate, mock_extract, mock_llm):
        mock_extract.return_value = WebsiteContent(
            url="https://example.com",
            title="Example Corp",
            meta_description="Leading tech company",
            headings=["Welcome to Example Corp"],
            paragraphs=["We provide software solutions."],
        )
        mock_llm.return_value = {
            "brand": {
                "name": "Example Corp",
                "category": "Technology",
                "summary": "A leading tech company.",
            },
            "analysis": {
                "competitor_analysis": {
                    "brand_overview": "Example Corp is a tech company.",
                    "main_category": "Technology",
                    "main_products_services": ["Software Development"],
                    "competitors": [
                        {
                            "name": "Competitor A",
                            "main_service": "Software",
                            "target_market": "Enterprise",
                            "key_strength": "Scale",
                            "weakness_or_gap": "Pricing",
                        }
                    ],
                    "brand_strengths": ["Innovation"],
                    "opportunities": ["Expand to new markets"],
                },
                "target_search_queries": [
                    {
                        "query": "best tech company",
                        "platforms": ["Google", "LinkedIn"],
                        "intent": "Service Discovery",
                        "business_relevance": "High",
                        "target_audience": "Business Owners",
                    }
                ],
                "seo_improvements": {
                    "primary_keyword": "technology services",
                    "secondary_keywords": ["software development"],
                    "long_tail_keywords": [
                        "best technology services company"
                    ],
                    "business_keywords": ["tech solutions"],
                    "recommended_title": (
                        "Example Corp | Leading Technology Services"
                    ),
                    "current_title": "Example Corp",
                    "title_improvement_notes": "Add keywords",
                    "meta_description": (
                        "Example Corp provides leading tech services."
                    ),
                    "business_summary": (
                        "A tech company offering software solutions."
                    ),
                    "supporting_content": [
                        {
                            "content_type": "Blog",
                            "title": "Top Tech Trends",
                            "description": "Blog about trends",
                        }
                    ],
                },
                "top_services": [
                    {
                        "service_name": "Software Development",
                        "description": "Custom software",
                        "target_industry": "Technology",
                        "target_customer": "Enterprises",
                        "main_benefit": "Efficiency",
                        "is_inferred": False,
                    }
                ],
                "target_audience": {
                    "primary_audience": [
                        {
                            "audience_label": "Enterprise",
                            "business_type": "Large Companies",
                            "requirement": "Custom Software",
                        }
                    ],
                    "secondary_audience": [],
                    "industry_segments": ["Technology"],
                    "customer_needs": ["Digital Transformation"],
                    "geographical_focus": "Global",
                    "customer_interests": ["Innovation"],
                    "recommended_marketing_segments": ["B2B Tech"],
                },
            },
        }

        response = client.post(
            "/link-analysis", json={"url": "https://example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["brand"]["name"] == "Example Corp"
        assert len(data["analysis"]["competitor_analysis"]["competitors"]) >= 1
        assert len(data["analysis"]["target_search_queries"]) >= 1
        assert data["analysis"]["seo_improvements"]["primary_keyword"] != ""
        assert len(data["analysis"]["top_services"]) >= 1
        assert len(data["analysis"]["target_audience"]["primary_audience"]) >= 1

