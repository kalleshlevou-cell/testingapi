# AI-Powered Website Link Analysis API

An intelligent FastAPI application that analyses any website URL using Google Gemini LLM to generate structured business insights across five dimensions: **competitor analysis**, **target search queries**, **SEO improvements**, **top services**, and **target audience identification**.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Sample API Request & Response](#sample-api-request--response)
- [Running Tests](#running-tests)
- [LLM Platform Comparison & Recommendation](#llm-platform-comparison--recommendation)
- [Cost Optimization Strategies](#cost-optimization-strategies)
- [Error Handling](#error-handling)
- [Security](#security)

---

## Features

- **Website Content Extraction** – Fetches and parses HTML using BeautifulSoup with lxml, extracting titles, meta tags, headings, paragraphs, links, and Open Graph data.
- **LLM-Powered Analysis** – Uses Google Gemini (gemini-2.5-flash) with structured JSON output mode for reliable, schema-conformant responses.
- **Five-Section Analysis** – Competitor intelligence, search query suggestions, SEO recommendations, service identification, and audience profiling.
- **SSRF Protection** – Validates URLs and blocks requests to private/reserved IP ranges.
- **Graceful Error Handling** – Returns meaningful error messages for inaccessible sites, invalid URLs, and LLM failures.
- **Fully Typed** – Pydantic v2 models for request/response validation.
- **Comprehensive Tests** – Unit tests with mocked dependencies.

---

## Architecture

```
Client Request
     │
     ▼
┌─────────────────────┐
│  FastAPI Endpoint    │
│  POST /link-analysis │
└──────────┬──────────┘
           │
     ┌─────▼─────┐
     │  Validate  │  ← SSRF protection, URL validation
     │    URL     │
     └─────┬─────┘
           │
  ┌────────▼────────┐
  │  Fetch Website  │  ← httpx async client
  │  HTML Content   │
  └────────┬────────┘
           │
  ┌────────▼────────┐
  │  Extract &      │  ← BeautifulSoup + lxml
  │  Clean Content  │
  └────────┬────────┘
           │
  ┌────────▼────────┐
  │  Gemini LLM     │  ← Structured JSON output
  │  Analysis       │
  └────────┬────────┘
           │
  ┌────────▼────────┐
  │  Validate &     │  ← Pydantic model mapping
  │  Return JSON    │
  └─────────────────┘
```

---

## Project Structure

```
ai-link-analysis/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app & endpoint
│   ├── config.py               # Settings from environment variables
│   ├── schemas.py              # Pydantic request/response models
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── website_extractor.py  # HTML fetching & content extraction
│   │   ├── llm_service.py        # Gemini LLM integration
│   │   ├── analysis_service.py   # Pipeline orchestration
│   │   └── competitor_service.py # Competitor helpers (extensible)
│   │
│   └── utils/
│       ├── __init__.py
│       └── validators.py       # URL validation & SSRF protection
│
├── tests/
│   ├── __init__.py
│   └── test_link_analysis.py   # Unit tests
│
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- A Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ai-link-analysis.git
cd ai-link-analysis
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GOOGLE_API_KEY=your_actual_api_key_here
```

---

## Running the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

The server will start at `http://localhost:4000`.

### API Documentation

- **Swagger UI:** http://localhost:4000/docs
- **ReDoc:** http://localhost:4000/redoc

---

## Sample API Request & Response

### Request

```bash
curl -X POST http://localhost:4000/link-analysis \
  -H "Content-Type: application/json" \
  -d '{"url": "https://stripe.com"}'
```

### Response (abbreviated)

```json
{
  "success": true,
  "website": "https://stripe.com",
  "brand": {
    "name": "Stripe",
    "category": "Financial Technology / Payments",
    "summary": "Stripe is a financial infrastructure platform for businesses, providing payment processing, billing, and financial tools for internet commerce."
  },
  "analysis": {
    "competitor_analysis": {
      "brand_overview": "Stripe provides a suite of APIs and tools that power online commerce for millions of businesses worldwide.",
      "main_category": "Financial Technology",
      "main_products_services": [
        "Online Payment Processing",
        "Billing & Subscriptions",
        "Revenue Recognition",
        "Fraud Prevention (Radar)",
        "Business Incorporation (Atlas)"
      ],
      "competitors": [
        {
          "name": "PayPal / Braintree",
          "main_service": "Payment Processing",
          "target_market": "SMBs & Enterprise",
          "key_strength": "Brand recognition and consumer trust",
          "weakness_or_gap": "Developer experience lags behind Stripe"
        },
        {
          "name": "Square (Block, Inc.)",
          "main_service": "POS & Online Payments",
          "target_market": "Small Businesses & Retail",
          "key_strength": "Strong physical POS ecosystem",
          "weakness_or_gap": "Less suited for complex online-only businesses"
        },
        {
          "name": "Adyen",
          "main_service": "Enterprise Payment Processing",
          "target_market": "Large Enterprise",
          "key_strength": "Unified global payment platform",
          "weakness_or_gap": "Higher barrier to entry for smaller businesses"
        }
      ],
      "brand_strengths": [
        "Best-in-class developer experience and API design",
        "Comprehensive financial infrastructure platform",
        "Global reach with local payment method support"
      ],
      "opportunities": [
        "Expand embedded finance offerings",
        "Grow in-person payment solutions",
        "Deepen AI-powered fraud prevention"
      ]
    },
    "target_search_queries": [
      {
        "query": "best online payment gateway for businesses",
        "platforms": ["Google", "LinkedIn"],
        "intent": "Service Discovery",
        "business_relevance": "Directly targets businesses looking for payment solutions",
        "target_audience": "Business owners and CTOs"
      },
      {
        "query": "payment processing API for developers",
        "platforms": ["Google", "X"],
        "intent": "Technical Research",
        "business_relevance": "Targets developer-led purchasing decisions",
        "target_audience": "Software developers and tech leads"
      },
      {
        "query": "accept payments online",
        "platforms": ["Google", "Facebook"],
        "intent": "Solution Search",
        "business_relevance": "Broad commercial intent query",
        "target_audience": "New business owners"
      },
      {
        "query": "subscription billing platform",
        "platforms": ["Google", "LinkedIn"],
        "intent": "Product Comparison",
        "business_relevance": "Targets SaaS and subscription businesses",
        "target_audience": "SaaS founders and finance teams"
      },
      {
        "query": "fintech payment solutions",
        "platforms": ["LinkedIn", "Instagram"],
        "intent": "Industry Research",
        "business_relevance": "Industry-level discovery",
        "target_audience": "Fintech professionals"
      }
    ],
    "seo_improvements": {
      "primary_keyword": "online payment processing",
      "secondary_keywords": ["payment gateway", "payment API", "accept payments online"],
      "long_tail_keywords": [
        "best payment processing API for startups",
        "how to accept credit card payments online"
      ],
      "business_keywords": ["fintech", "billing platform", "revenue automation"],
      "recommended_title": "Stripe – Online Payment Processing & Financial Infrastructure for Businesses",
      "meta_description": "Stripe provides payment processing APIs, billing tools, and financial infrastructure that power commerce for millions of businesses worldwide. Start accepting payments today.",
      "supporting_content": [
        {
          "content_type": "Blog",
          "title": "How to Choose the Right Payment Gateway",
          "description": "Educational content to capture top-of-funnel search traffic."
        },
        {
          "content_type": "FAQ Page",
          "title": "Payment Processing FAQs",
          "description": "Addresses common questions about fees, security, and integration."
        }
      ]
    },
    "top_services": [
      {
        "service_name": "Payments",
        "description": "Accept online and in-person payments with a fully integrated suite of payment products.",
        "target_industry": "E-commerce, SaaS, Marketplaces",
        "target_customer": "Online businesses of all sizes",
        "main_benefit": "Increase conversion rates with optimised checkout",
        "is_inferred": false
      }
    ],
    "target_audience": {
      "primary_audience": [
        {
          "audience_label": "Online Businesses",
          "business_type": "E-commerce & SaaS",
          "requirement": "Reliable payment processing"
        }
      ],
      "secondary_audience": [
        {
          "audience_label": "Enterprise Finance Teams",
          "business_type": "Large Corporations",
          "requirement": "Revenue recognition & billing automation"
        }
      ],
      "industry_segments": ["E-commerce", "SaaS", "Fintech", "Marketplaces"],
      "customer_needs": ["Payment processing", "Fraud prevention", "Global expansion"],
      "geographical_focus": "Global (with strong US and European presence)",
      "customer_interests": ["API-first tools", "Developer experience", "Financial automation"],
      "recommended_marketing_segments": ["Startup Founders", "CTOs", "E-commerce Managers"]
    }
  }
}
```

> **Note:** The above is an illustrative sample. Actual responses will vary based on the analysed website.

---

## Running Tests

```bash
pytest tests/ -v
```

Expected output:

```
tests/test_link_analysis.py::TestHealthCheck::test_health_endpoint PASSED
tests/test_link_analysis.py::TestURLValidation::test_empty_url PASSED
tests/test_link_analysis.py::TestURLValidation::test_invalid_scheme PASSED
tests/test_link_analysis.py::TestURLValidation::test_localhost_blocked PASSED
tests/test_link_analysis.py::TestURLValidation::test_private_ip_blocked PASSED
tests/test_link_analysis.py::TestURLValidation::test_valid_url PASSED
tests/test_link_analysis.py::TestAPIInputValidation::test_missing_url PASSED
tests/test_link_analysis.py::TestAPIInputValidation::test_invalid_url_format PASSED
tests/test_link_analysis.py::TestWebsiteContent::test_to_prompt_text PASSED
tests/test_link_analysis.py::TestWebsiteContent::test_to_prompt_text_truncation PASSED
tests/test_link_analysis.py::TestLinkAnalysisPipeline::test_successful_analysis PASSED
```

---

## LLM Platform Comparison & Recommendation

### A. LLM Platform Comparison

| Criteria | Google Gemini | OpenAI | Anthropic Claude |
|---|---|---|---|
| **Provider** | Google DeepMind | OpenAI | Anthropic |
| **Recommended Model** | gemini-2.5-flash | gpt-4o-mini | claude-3.5-haiku |
| **Input Cost** | \$0.15 / 1M tokens | \$0.15 / 1M tokens | \$0.80 / 1M tokens |
| **Output Cost** | \$0.60 / 1M tokens | \$0.60 / 1M tokens | \$4.00 / 1M tokens |
| **Response Speed** | ~3-8 seconds | ~5-12 seconds | ~5-15 seconds |
| **Context Window** | 1,048,576 tokens | 128,000 tokens | 200,000 tokens |
| **JSON Mode** | ✅ Native (`response_mime_type`) | ✅ Native (`response_format`) | ⚠️ Prompt-based |
| **Accuracy** | Excellent for content understanding | Excellent | Excellent |
| **Free Tier** | ✅ Generous free tier | ❌ No free tier | ❌ No free tier |

> **Note:** Pricing is based on current published rates as of November 2026. Response speed estimates are based on typical API latency for content of this size (~2,000-5,000 tokens input). These are estimates, not benchmarked measurements.

### B. Best Model Selection: Google Gemini 2.5 Flash

**Selected Model:** `gemini-2.5-flash`

**Reasons:**

1. **Cost-Effective** – At \$0.15/1M input tokens and \$0.60/1M output tokens, Gemini 2.5 Flash matches the cheapest tier while outperforming on context window.
2. **Massive Context Window** – 1M tokens means even the largest websites can be processed without truncation. Other models cap at 128K-200K.
3. **Native JSON Output** – Setting `response_mime_type="application/json"` guarantees valid JSON output, eliminating parsing failures.
4. **Fast Response Time** – Optimised for speed; typical responses arrive in 3-8 seconds.
5. **High Accuracy** – Strong performance on content understanding, competitive analysis, and structured reasoning tasks.
6. **Free Tier Available** – Generous free quota for development and testing, reducing iteration costs.

### C. Cost Estimation Per Analysis

| Metric | Estimate |
|---|---|
| **Average Input Tokens** | ~3,000 tokens (cleaned website content + prompt) |
| **Average Output Tokens** | ~2,000 tokens (structured JSON response) |
| **Cost per Analysis** | ~\$0.0017 (input: \$0.00045 + output: \$0.0012) |
| **Analyses per \$1** | ~588 |
| **Expected Response Time** | 3-8 seconds |

### D. Alternative / Fallback Model

| | Primary | Fallback |
|---|---|---|
| **Provider** | Google Gemini | OpenAI |
| **Model** | gemini-2.5-flash | gpt-4o-mini |
| **Use When** | Default – all analyses | Gemini API downtime |

---

## Cost Optimization Strategies

The following strategies are implemented or recommended to minimise LLM API costs:

### Implemented in This Application

1. **HTML Cleaning** – Scripts, styles, SVGs, iframes, and noscript tags are stripped before content extraction, reducing token count by 40-70%.
2. **Content Truncation** – Website content is capped at 50,000 characters (configurable via `MAX_CONTENT_LENGTH`) to prevent excessive token usage.
3. **Structured Extraction** – Only meaningful elements (titles, meta tags, headings, paragraphs, links) are extracted rather than raw HTML.
4. **Low Temperature** – `temperature=0.3` reduces randomness and encourages concise, deterministic responses.
5. **JSON Output Mode** – Native `response_mime_type="application/json"` eliminates wasted tokens on markdown formatting or commentary.
6. **Deduplication** – Duplicate links and empty content are filtered before sending to the LLM.

### Recommended for Production

7. **Response Caching** – Cache LLM responses by URL with a configurable TTL (e.g., 24 hours) using Redis or an in-memory store to avoid re-analysing the same site.
8. **Tiered Analysis** – Use a smaller/cheaper model (e.g., gemini-2.5-flash-lite) for simple extraction tasks and the full model only for complex analysis.
9. **Batch Processing** – When analysing multiple URLs, batch requests to amortise overhead.
10. **Prompt Optimisation** – Continuously refine prompts to reduce input tokens while maintaining output quality.

---

## Error Handling

| Scenario | HTTP Status | Detail |
|---|---|---|
| Invalid URL format | 422 | Pydantic validation error |
| URL to private/reserved IP | 400 | SSRF protection message |
| Unresolvable hostname | 400 | DNS resolution failure |
| Website returns HTTP error | 502 | HTTP status code from site |
| Website unreachable / timeout | 502 | Network error type |
| LLM returns invalid JSON | 500 | JSON parsing error detail |
| LLM API failure | 500 | LLM error message |

---

## Security

- **SSRF Protection** – All URLs are resolved and checked against private/reserved IP ranges (RFC 1918, RFC 5737, loopback, link-local, multicast) before any HTTP request is made.
- **No Credential Exposure** – API keys are loaded from environment variables via `.env` file (excluded from version control via `.gitignore`).
- **Input Validation** – Pydantic enforces `HttpUrl` type validation on all incoming URLs.
- **TLS Verification** – HTTP client enforces TLS certificate verification (`verify=True`).

---

## License

MIT

---

**Built with ❤️ using FastAPI + Google Gemini**

