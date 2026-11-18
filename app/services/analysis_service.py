"""High-level orchestration: fetch site -> LLM -> structured response."""

from __future__ import annotations

import logging
from typing import Any

from app.config import Settings
from app.schemas import (
    Analysis,
    AudienceSegment,
    BrandInfo,
    Competitor,
    CompetitorAnalysis,
    LinkAnalysisResponse,
    SearchQuery,
    SEOImprovements,
    Service,
    SupportingContent,
    TargetAudience,
)
from app.services.website_extractor import extract_website_content
from app.services.llm_service import analyse_with_llm

logger = logging.getLogger(__name__)


def _parse_competitors(raw: list[dict] | None) -> list[Competitor]:
    if not raw:
        return []
    return [
        Competitor(
            name=c.get("name", ""),
            main_service=c.get("main_service", ""),
            target_market=c.get("target_market", ""),
            key_strength=c.get("key_strength", ""),
            weakness_or_gap=c.get("weakness_or_gap", ""),
        )
        for c in raw
    ]


def _parse_search_queries(raw: list[dict] | None) -> list[SearchQuery]:
    if not raw:
        return []
    return [
        SearchQuery(
            query=q.get("query", ""),
            platforms=q.get("platforms", []),
            intent=q.get("intent", ""),
            business_relevance=q.get("business_relevance", ""),
            target_audience=q.get("target_audience", ""),
        )
        for q in raw
    ]


def _parse_supporting_content(raw: list[dict] | None) -> list[SupportingContent]:
    if not raw:
        return []
    return [
        SupportingContent(
            content_type=s.get("content_type", ""),
            title=s.get("title", ""),
            description=s.get("description", ""),
        )
        for s in raw
    ]


def _parse_services(raw: list[dict] | None) -> list[Service]:
    if not raw:
        return []
    return [
        Service(
            service_name=s.get("service_name", ""),
            description=s.get("description", ""),
            target_industry=s.get("target_industry", ""),
            target_customer=s.get("target_customer", ""),
            main_benefit=s.get("main_benefit", ""),
            is_inferred=s.get("is_inferred", False),
        )
        for s in raw
    ]


def _parse_audience_segments(raw: list[dict] | None) -> list[AudienceSegment]:
    if not raw:
        return []
    return [
        AudienceSegment(
            audience_label=a.get("audience_label", ""),
            business_type=a.get("business_type", ""),
            requirement=a.get("requirement", ""),
        )
        for a in raw
    ]


def _build_response(url: str, data: dict) -> LinkAnalysisResponse:
    """Map the raw LLM JSON dict into validated Pydantic models."""

    brand_raw = data.get("brand", {})
    brand = BrandInfo(
        name=brand_raw.get("name", ""),
        category=brand_raw.get("category", ""),
        summary=brand_raw.get("summary", ""),
    )

    a = data.get("analysis", {})

    # Section 1 - Competitor Analysis
    ca = a.get("competitor_analysis", {})
    competitor_analysis = CompetitorAnalysis(
        brand_overview=ca.get("brand_overview", ""),
        main_category=ca.get("main_category", ""),
        main_products_services=ca.get("main_products_services", []),
        competitors=_parse_competitors(ca.get("competitors")),
        brand_strengths=ca.get("brand_strengths", []),
        opportunities=ca.get("opportunities", []),
    )

    # Section 2 - Target Search Queries
    target_search_queries = _parse_search_queries(a.get("target_search_queries"))

    # Section 3 - SEO Improvements
    seo_raw = a.get("seo_improvements", {})
    seo = SEOImprovements(
        primary_keyword=seo_raw.get("primary_keyword", ""),
        secondary_keywords=seo_raw.get("secondary_keywords", []),
        long_tail_keywords=seo_raw.get("long_tail_keywords", []),
        business_keywords=seo_raw.get("business_keywords", []),
        recommended_title=seo_raw.get("recommended_title", ""),
        current_title=seo_raw.get("current_title", ""),
        title_improvement_notes=seo_raw.get("title_improvement_notes", ""),
        meta_description=seo_raw.get("meta_description", ""),
        business_summary=seo_raw.get("business_summary", ""),
        supporting_content=_parse_supporting_content(
            seo_raw.get("supporting_content")
        ),
    )

    # Section 4 - Top Services
    top_services = _parse_services(a.get("top_services"))

    # Section 5 - Target Audience
    ta_raw = a.get("target_audience", {})
    target_audience = TargetAudience(
        primary_audience=_parse_audience_segments(ta_raw.get("primary_audience")),
        secondary_audience=_parse_audience_segments(ta_raw.get("secondary_audience")),
        industry_segments=ta_raw.get("industry_segments", []),
        customer_needs=ta_raw.get("customer_needs", []),
        geographical_focus=ta_raw.get("geographical_focus", ""),
        customer_interests=ta_raw.get("customer_interests", []),
        recommended_marketing_segments=ta_raw.get(
            "recommended_marketing_segments", []
        ),
    )

    analysis = Analysis(
        competitor_analysis=competitor_analysis,
        target_search_queries=target_search_queries,
        seo_improvements=seo,
        top_services=top_services,
        target_audience=target_audience,
    )

    return LinkAnalysisResponse(
        success=True,
        website=url,
        brand=brand,
        analysis=analysis,
    )


async def perform_link_analysis(
    url: str, settings: Settings
) -> LinkAnalysisResponse:
    """Full pipeline: extract -> LLM -> structured response."""

    # Step 1 - Fetch & extract
    logger.info("Extracting content from %s", url)
    content = await extract_website_content(url, timeout=settings.request_timeout)

    # Step 2 - Build prompt text (cleaned, truncated)
    prompt_text = content.to_prompt_text(max_chars=settings.max_content_length)
    logger.info(
        "Extracted %d chars of prompt text (HTML was %d bytes)",
        len(prompt_text),
        content.raw_html_length,
    )

    # Step 3 - LLM analysis
    logger.info("Sending content to LLM (%s)...", settings.llm_model)
    llm_result = await analyse_with_llm(prompt_text, settings)

    # Step 4 - Build validated response
    response = _build_response(url, llm_result)
    return response

