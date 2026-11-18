"""Pydantic models for request/response validation."""

from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


# ── Request ──────────────────────────────────────────────────────────────────
class LinkAnalysisRequest(BaseModel):
    """Incoming request with a URL to analyse."""

    url: HttpUrl = Field(
        ...,
        description="Website URL to analyse",
        examples=["https://example.com"],
    )


# ── Competitor Analysis ──────────────────────────────────────────────────────
class Competitor(BaseModel):
    name: str = Field(..., description="Competitor brand name")
    main_service: str = Field(default="", description="Primary service offered")
    target_market: str = Field(default="", description="Primary target market")
    key_strength: str = Field(default="", description="Key competitive strength")
    weakness_or_gap: str = Field(default="", description="Weakness or market gap")


class CompetitorAnalysis(BaseModel):
    brand_overview: str = Field(default="", description="Overview of the submitted brand")
    main_category: str = Field(default="", description="Main business category")
    main_products_services: list[str] = Field(default_factory=list)
    competitors: list[Competitor] = Field(default_factory=list)
    brand_strengths: list[str] = Field(
        default_factory=list, description="Your brand competitive advantages"
    )
    opportunities: list[str] = Field(
        default_factory=list, description="Market positioning opportunities"
    )


# ── Target Search Queries ────────────────────────────────────────────────────
class SearchQuery(BaseModel):
    query: str = Field(..., description="Suggested search query")
    platforms: list[str] = Field(default_factory=list, description="Relevant platforms")
    intent: str = Field(default="", description="Search intent category")
    business_relevance: str = Field(default="", description="Why this query matters")
    target_audience: str = Field(default="", description="Who would search this")


# ── SEO Improvements ────────────────────────────────────────────────────────
class SupportingContent(BaseModel):
    content_type: str = Field(..., description="Type of content (e.g., blog, FAQ)")
    title: str = Field(default="", description="Suggested title or topic")
    description: str = Field(default="", description="Brief description")


class SEOImprovements(BaseModel):
    primary_keyword: str = Field(default="")
    secondary_keywords: list[str] = Field(default_factory=list)
    long_tail_keywords: list[str] = Field(default_factory=list)
    business_keywords: list[str] = Field(default_factory=list)
    recommended_title: str = Field(default="")
    current_title: str = Field(default="")
    title_improvement_notes: str = Field(default="")
    meta_description: str = Field(default="")
    business_summary: str = Field(default="")
    supporting_content: list[SupportingContent] = Field(default_factory=list)


# ── Top Services ─────────────────────────────────────────────────────────────
class Service(BaseModel):
    service_name: str = Field(...)
    description: str = Field(default="")
    target_industry: str = Field(default="")
    target_customer: str = Field(default="")
    main_benefit: str = Field(default="")
    is_inferred: bool = Field(
        default=False, description="True if not directly found on site"
    )


# ── Target Audience ──────────────────────────────────────────────────────────
class AudienceSegment(BaseModel):
    audience_label: str = Field(...)
    business_type: str = Field(default="")
    requirement: str = Field(default="")


class TargetAudience(BaseModel):
    primary_audience: list[AudienceSegment] = Field(default_factory=list)
    secondary_audience: list[AudienceSegment] = Field(default_factory=list)
    industry_segments: list[str] = Field(default_factory=list)
    customer_needs: list[str] = Field(default_factory=list)
    geographical_focus: str = Field(default="")
    customer_interests: list[str] = Field(default_factory=list)
    recommended_marketing_segments: list[str] = Field(default_factory=list)


# ── Full Analysis ────────────────────────────────────────────────────────────
class Analysis(BaseModel):
    competitor_analysis: CompetitorAnalysis = Field(default_factory=CompetitorAnalysis)
    target_search_queries: list[SearchQuery] = Field(default_factory=list)
    seo_improvements: SEOImprovements = Field(default_factory=SEOImprovements)
    top_services: list[Service] = Field(default_factory=list)
    target_audience: TargetAudience = Field(default_factory=TargetAudience)


# ── Brand Info ───────────────────────────────────────────────────────────────
class BrandInfo(BaseModel):
    name: str = Field(default="")
    category: str = Field(default="")
    summary: str = Field(default="")


# ── Top-Level Response ───────────────────────────────────────────────────────
class LinkAnalysisResponse(BaseModel):
    success: bool = True
    website: str
    brand: BrandInfo = Field(default_factory=BrandInfo)
    analysis: Analysis = Field(default_factory=Analysis)


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    website: str = ""

