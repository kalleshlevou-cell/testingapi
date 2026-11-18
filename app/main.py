"""FastAPI application entry-point for the AI Link Analysis API."""

from __future__ import annotations

import logging

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, Settings
from app.schemas import LinkAnalysisRequest, LinkAnalysisResponse, ErrorResponse
from app.services.analysis_service import perform_link_analysis
from app.utils.validators import validate_url, URLValidationError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Link Analysis API",
    description=(
        "Analyse a website URL using an LLM to generate business, competitor, "
        "SEO, search-query, and target-audience insights."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "AI Link Analysis API is running."}


@app.post(
    "/link-analysis",
    response_model=LinkAnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        502: {"model": ErrorResponse, "description": "Website unreachable"},
        500: {"model": ErrorResponse, "description": "Internal / LLM error"},
    },
    tags=["Analysis"],
    summary="Analyse a website URL",
    description=(
        "Accepts a website URL, extracts its content, analyses it with an LLM, "
        "and returns structured insights across five sections: competitor analysis, "
        "target search queries, SEO improvements, top services, and target audience."
    ),
)
async def link_analysis(
    request: LinkAnalysisRequest,
    settings: Settings = Depends(get_settings),
):
    """Main analysis endpoint."""
    url = str(request.url)

    # 1. Validate URL & SSRF protection
    try:
        validated_url = validate_url(url)
    except URLValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # 2. Run the full pipeline
    try:
        result = await perform_link_analysis(validated_url, settings)
        return result
    except httpx.HTTPStatusError as exc:
        logger.error("HTTP error fetching %s: %s", url, exc)
        raise HTTPException(
            status_code=502,
            detail=(
                f"Could not fetch website (HTTP {exc.response.status_code}). "
                "The site may be down or blocking automated access."
            ),
        )
    except httpx.RequestError as exc:
        logger.error("Network error fetching %s: %s", url, exc)
        raise HTTPException(
            status_code=502,
            detail=(
                f"Could not reach the website: {type(exc).__name__}. "
                "Please check the URL and try again."
            ),
        )
    except ValueError as exc:
        logger.error("LLM processing error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"LLM analysis failed: {exc}",
        )
    except Exception as exc:
        logger.exception("Unexpected error analysing %s", url)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {type(exc).__name__}: {exc}",
        )

