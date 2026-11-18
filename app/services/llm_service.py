"""Google Gemini LLM integration for website analysis."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from google import genai
from google.genai import types

from app.config import Settings

logger = logging.getLogger(__name__)


def _build_client(settings: Settings) -> genai.Client:
    """Create a Gemini client with the configured API key."""
    return genai.Client(api_key=settings.google_api_key)


_SYSTEM_INSTRUCTION = """You are an expert business analyst specialising in competitive intelligence, SEO, digital marketing, and audience research.

You will receive extracted content from a website. Analyse it thoroughly and produce a structured JSON report with these five sections:

1. **competitor_analysis** – Identify the brand, its category, main products/services, at least 3 competitors (with strengths and weaknesses), the brand's own strengths, and market opportunities.
2. **target_search_queries** – 5 search queries potential customers would use. Each must include the query text, relevant platforms (from Google, Facebook, Instagram, LinkedIn, X/Twitter), search intent, business relevance, and target audience.
3. **seo_improvements** – Primary keyword, secondary keywords, long-tail keywords, business keywords, a recommended SEO title, recommended meta description, a short business summary, and at least 5 supporting content suggestions (blogs, FAQs, landing pages, etc.).
4. **top_services** – The 5 most important services found on the website. Mark any inferred service with "is_inferred": true.
5. **target_audience** – Primary and secondary audience segments, industry segments, customer needs, geographical focus (if available), customer interests, and recommended marketing segments.

IMPORTANT RULES:
- Base your analysis on the actual website content provided. Do NOT fabricate information.
- Competitor information should be based on credible general knowledge about the industry. Clearly label any AI-inferred suggestions.
- Do NOT invent search volumes or ranking data.
- Return ONLY valid JSON matching the schema below — no markdown, no commentary, no code fences.
"""

_JSON_SCHEMA_HINT = """{
  "brand": {
    "name": "<string>",
    "category": "<string>",
    "summary": "<string>"
  },
  "analysis": {
    "competitor_analysis": {
      "brand_overview": "<string>",
      "main_category": "<string>",
      "main_products_services": ["<string>"],
      "competitors": [
        {
          "name": "<string>",
          "main_service": "<string>",
          "target_market": "<string>",
          "key_strength": "<string>",
          "weakness_or_gap": "<string>"
        }
      ],
      "brand_strengths": ["<string>"],
      "opportunities": ["<string>"]
    },
    "target_search_queries": [
      {
        "query": "<string>",
        "platforms": ["<string>"],
        "intent": "<string>",
        "business_relevance": "<string>",
        "target_audience": "<string>"
      }
    ],
    "seo_improvements": {
      "primary_keyword": "<string>",
      "secondary_keywords": ["<string>"],
      "long_tail_keywords": ["<string>"],
      "business_keywords": ["<string>"],
      "recommended_title": "<string>",
      "current_title": "<string>",
      "title_improvement_notes": "<string>",
      "meta_description": "<string>",
      "business_summary": "<string>",
      "supporting_content": [
        {
          "content_type": "<string>",
          "title": "<string>",
          "description": "<string>"
        }
      ]
    },
    "top_services": [
      {
        "service_name": "<string>",
        "description": "<string>",
        "target_industry": "<string>",
        "target_customer": "<string>",
        "main_benefit": "<string>",
        "is_inferred": false
      }
    ],
    "target_audience": {
      "primary_audience": [
        {"audience_label": "<string>", "business_type": "<string>", "requirement": "<string>"}
      ],
      "secondary_audience": [
        {"audience_label": "<string>", "business_type": "<string>", "requirement": "<string>"}
      ],
      "industry_segments": ["<string>"],
      "customer_needs": ["<string>"],
      "geographical_focus": "<string>",
      "customer_interests": ["<string>"],
      "recommended_marketing_segments": ["<string>"]
    }
  }
}"""


async def analyse_with_llm(
    website_text: str, settings: Settings
) -> dict[str, Any]:
    """Send extracted website content to Gemini and return structured analysis.

    Returns the parsed JSON dict or raises on failure.
    """
    client = _build_client(settings)

    user_prompt = (
        f"Analyse the following website content and produce the JSON report.\n\n"
        f"--- WEBSITE CONTENT START ---\n{website_text}\n--- WEBSITE CONTENT END ---\n\n"
        f"Respond with ONLY valid JSON matching this schema:\n{_JSON_SCHEMA_HINT}"
    )

    response = client.models.generate_content(
        model=settings.llm_model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_INSTRUCTION,
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )

    raw_text = response.text
    if not raw_text:
        raise ValueError("LLM returned an empty response.")

    # Strip possible markdown code fences (safety net)
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
        raw_text = re.sub(r"```\s*$", "", raw_text)

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned invalid JSON: %s", raw_text[:500])
        raise ValueError(f"LLM returned invalid JSON: {exc}") from exc

    return data

