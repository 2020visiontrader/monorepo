# Architecture Overview

## System Architecture

### Backend (Django)

**Tech Stack:**
- Django 5.0 + Django REST Framework
- PostgreSQL for primary database
- Redis for caching and Celery broker
- Celery for background tasks
- Pydantic for LLM output validation
- httpx for HTTP requests

**Key Components:**

1. **Core App** - Multitenancy & RBAC
   - Organization and User models
   - Role-based access control (ORG_ADMIN, BRAND_MANAGER, EDITOR, VIEWER)
   - Tenancy middleware for org/brand scoping

2. **Brands App** - Brand Management
   - Brand, BrandProfile, Pathway models
   - Onboarding wizard endpoints
   - Site blueprint generation

3. **Competitors App** - Competitor Analysis
   - CompetitorProfile, CrawlRun, IASignature, PageNode
   - Heuristic parser for competitor sites
   - Sitemap-first crawling with nav fallback

4. **Content App** - Content Generation
   - ProductDraft, ContentVariant, PublishJob
   - LLM-powered content generation
   - Shopify publishing with idempotency

5. **SEO App** - SEO Optimization
   - SEOPlan, KeywordSeedSet
   - Title, meta, H1-H3, alt text, JSON-LD generation
   - Keyword clustering

6. **Frameworks App** - Marketing Frameworks
   - FrameworkCandidate, Framework, FrameworkUsageLog
   - Curated library of 15-30 frameworks
   - Framework ingestion and approval workflow

7. **Shopify App** - Shopify Integration
   - OAuth flow for store connection
   - API client with idempotency keys
   - Product, page, metafield updates

8. **LLM App** - LLM Abstraction
   - Provider interface (Mock, OpenAI, Anthropic)
   - Pydantic schemas for validation
   - Cost and latency tracking

9. **Store Templates App** - Template Management
   - Template, TemplateVariant models
   - Template generation, upload, customization

### Frontend (Next.js)

**Tech Stack:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Radix UI / Headless UI
- Framer Motion
- Lucide Icons

**Key Features:**

1. **Premium App Shell**
   - TopNav with brand switcher
   - LeftNav with collapsible sections
   - RightPanel for contextual actions
   - Consistent spacing and typography

2. **Pages:**
   - Dashboard
   - Onboarding Wizard (5-step)
   - Competitor Insights
   - Build My Site (Site Blueprint)
   - PDP Copy Review
   - SEO Optimize
   - Frameworks Curation
   - Store Templates (Gallery, Preview, Customize, Generate, Upload)
   - Jobs Monitor
   - Settings & Pathways

3. **Store Templates Module:**
   - Template Gallery with filters
   - Template Preview with device toggles
   - Customization interface (tokens, sections, SEO)
   - AI template generation
   - Template upload with validation

## Data Flow

### Content Generation Flow

1. User completes onboarding → BrandProfile created
2. User adds competitors → CompetitorProfile created → Crawl triggered
3. Crawl completes → IA_Signature and PageNodes created
4. User generates blueprint → LLM generates from BrandProfile + IA_Signatures
5. User selects products → Content generation triggered
6. LLM generates variants (max 3) → ContentVariant created
7. User reviews and accepts → PublishJob created
8. Celery task publishes to Shopify → AuditLog created

### SEO Optimization Flow

1. Keyword seeds extracted from competitors and brand content
2. Keywords clustered
3. SEO generation triggered → LLM generates titles/meta/headers/etc.
4. SEOPlan created with proposals
5. User reviews and publishes → PublishJob created
6. Celery task updates Shopify → AuditLog created

## Limits & Constraints

- `MAX_VARIANTS = 3` - Maximum content variants per product
- `MAX_COMPETITOR_PAGES = 10` - Default max pages per competitor
- `MAX_COMPETITOR_PAGES_SINGLE_SKU = 5` - Max pages for single-SKU brands

## Security

- Multitenancy enforced at middleware level
- RBAC checks on all API endpoints
- Shopify OAuth with secure token storage
- Idempotency keys for all Shopify writes
- Audit logging for all publish operations

## Scalability

- Celery workers for async processing
- Redis for caching and rate limiting
- Database indexes on foreign keys and common queries
- Background job tracking for long-running tasks

## Testing Strategy

- Unit tests for parsers, validators, selection logic
- Integration tests with HTML fixtures
- Contract tests for Shopify API
- Snapshot tests for LLM outputs (via mock)
- E2E tests with Playwright

## Deployment

- Docker containers for all services
- Docker Compose for local development
- Environment-specific configs (ST/SIT/UAT/PROD)
- Feature flags for gradual rollout
- CI/CD pipeline with GitHub Actions

