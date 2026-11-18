# AI Link Analysis API

A FastAPI application that analyses a website URL using Google Gemini LLM and returns structured business, competitor, SEO, search query, and target audience insights.

## Live Demo

| | URL |
|---|---|
| **Live API** | https://testingapi-1-srom.onrender.com |
| **API Endpoint** | https://testingapi-1-srom.onrender.com/link-analysis |
| **API Documentation** | https://testingapi-1-srom.onrender.com/docs |

---

## Features

- Accepts a website URL and fetches its content
- Extracts and cleans HTML content using BeautifulSoup
- Analyses content using Google Gemini LLM
- Returns structured JSON with 5 analysis sections:
  1. Competitor Analysis
  2. Top 5 Target Search Queries
  3. SEO Improvements
  4. Top 5 Services
  5. Target Audience Identification
- SSRF protection and URL validation
- Graceful error handling for inaccessible websites and invalid URLs

---

## Tech Stack

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- HTTPX
- BeautifulSoup4
- Google Gemini API (`google-genai`)

---

## Project Structure

```
ai-link-analysis/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   │
│   ├── services/
│   │   ├── website_extractor.py
│   │   ├── llm_service.py
│   │   ├── analysis_service.py
│   │   └── competitor_service.py
│   │
│   └── utils/
│       └── validators.py
│
├── tests/
│   └── test_link_analysis.py
│
├── .env.example
├── .python-version
├── requirements.txt
└── README.md
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/kalleshlevou-cell/testingapi.git
cd testingapi
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your Gemini API key:

```bash
cp .env.example .env
```

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get a free API key at: https://aistudio.google.com/apikey

### 5. Run the server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 4000
```

API will be available at: http://127.0.0.1:4000

---

## API Usage

### Endpoint

```
POST /link-analysis
```

### Request

```json
{
  "url": "https://vercel.com"
}
```

### Sample Response

```json
{
  "success": true,
  "website": "https://vercel.com",
  "brand": {
    "name": "Vercel",
    "category": "Cloud Platform / Developer Tools",
    "summary": "Vercel is a cloud platform for frontend developers, providing tools to deploy and scale web applications."
  },
  "analysis": {
    "competitor_analysis": {
      "brand_overview": "Vercel is a leading cloud platform focused on frontend deployment and serverless functions.",
      "main_category": "Cloud Hosting & Deployment",
      "main_products_services": ["Frontend Deployment", "Serverless Functions", "Edge Network", "Analytics"],
      "competitors": [
        {
          "name": "Netlify",
          "main_service": "Web Hosting & Deployment",
          "target_market": "Frontend Developers",
          "key_strength": "Easy CI/CD integration",
          "weakness_or_gap": "Limited serverless capabilities"
        }
      ],
      "brand_strengths": ["Next.js integration", "Global edge network", "Zero-config deployments"],
      "opportunities": ["Expand into backend services", "Target enterprise customers"]
    },
    "target_search_queries": [
      {
        "query": "best frontend deployment platform",
        "platforms": ["Google", "LinkedIn"],
        "intent": "Service Discovery",
        "business_relevance": "Direct match to Vercel's core offering",
        "target_audience": "Frontend developers and startups"
      }
    ],
    "seo_improvements": {
      "primary_keyword": "frontend deployment platform",
      "secondary_keywords": ["serverless hosting", "Next.js hosting", "edge deployment"],
      "long_tail_keywords": ["best platform to deploy Next.js apps", "free frontend hosting for developers"],
      "business_keywords": ["Vercel hosting", "cloud deployment", "jamstack platform"],
      "recommended_title": "Vercel – The Frontend Cloud for Developers | Deploy, Scale & Optimise",
      "meta_description": "Deploy your frontend apps instantly with Vercel. Serverless functions, edge network, and seamless Next.js integration. Start for free.",
      "supporting_content": [
        {
          "content_type": "Blog",
          "title": "How to Deploy a Next.js App on Vercel in 5 Minutes",
          "description": "Step-by-step guide targeting developers searching for Next.js deployment tutorials."
        }
      ]
    },
    "top_services": [
      {
        "service_name": "Frontend Deployment",
        "description": "Instant deployment of frontend applications from Git.",
        "target_industry": "Technology",
        "target_customer": "Frontend Developers",
        "main_benefit": "Zero-config deployments with global CDN",
        "is_inferred": false
      }
    ],
    "target_audience": {
      "primary_audience": [
        {
          "audience_label": "Frontend Developers",
          "business_type": "Individual / Agency",
          "requirement": "Fast and reliable deployment platform"
        }
      ],
      "secondary_audience": [
        {
          "audience_label": "Startups",
          "business_type": "Early-stage companies",
          "requirement": "Scalable hosting with minimal DevOps"
        }
      ],
      "industry_segments": ["Technology", "E-commerce", "SaaS"],
      "customer_needs": ["Fast deployments", "Global performance", "Easy CI/CD"],
      "geographical_focus": "Global",
      "customer_interests": ["Web performance", "Developer experience", "Serverless architecture"],
      "recommended_marketing_segments": ["Frontend developers", "JavaScript developers", "Next.js community"]
    }
  }
}
```

---

## LLM Platform Research & Recommendation

### Model Comparison

| Criteria | Google Gemini 2.5 Flash | OpenAI GPT-4o Mini | Anthropic Claude Haiku |
|---|---|---|---|
| **Provider** | Google | OpenAI | Anthropic |
| **API Cost (Input)** | $0.075 / 1M tokens | $0.15 / 1M tokens | $0.25 / 1M tokens |
| **API Cost (Output)** | $0.30 / 1M tokens | $0.60 / 1M tokens | $1.25 / 1M tokens |
| **Response Speed** | Fast (~5-10s) | Fast (~5-10s) | Moderate (~8-15s) |
| **Context Window** | 1M tokens | 128K tokens | 200K tokens |
| **JSON Support** | Native (`response_mime_type`) | Function calling | Tool use |
| **Accuracy** | High | High | High |
| **Recommendation** | ✅ Best choice | Good alternative | Higher cost |

### Recommended Model: **Google Gemini 2.5 Flash**

**Reasons:**
- Lowest API cost among comparable models
- Native JSON output mode eliminates parsing errors
- 1M token context window handles large websites easily
- Fast response time suitable for real-time API use
- Free tier available for development and testing

### Estimated Cost Per Analysis

| Item | Estimate |
|---|---|
| Input tokens (website content + prompt) | ~3,000 tokens |
| Output tokens (full JSON response) | ~1,500 tokens |
| **Cost per request** | **~$0.00067** |

### Cost Optimisation Strategies

1. Clean HTML before sending — strip scripts, styles, and hidden elements
2. Truncate content to the most relevant sections (title, headings, paragraphs)
3. Use `response_mime_type="application/json"` to avoid extra output tokens
4. Cache results for previously analysed URLs
5. Use Gemini Flash (not Pro) for standard analysis tasks
6. Limit prompt length by extracting only visible text

### Fallback Model

**OpenAI GPT-4o Mini** — reliable JSON output, wide availability, slightly higher cost.

---

## Error Handling

| Scenario | HTTP Status | Response |
|---|---|---|
| Invalid URL | 400 | `{"success": false, "error": "..."}` |
| Private/internal IP (SSRF) | 400 | `{"success": false, "error": "..."}` |
| Website unreachable / 403 | 502 | `{"success": false, "error": "..."}` |
| LLM failure | 500 | `{"success": false, "error": "..."}` |

---

## Running Tests

```bash
pytest tests/
```
