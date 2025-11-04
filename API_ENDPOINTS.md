# Phase-1 API Endpoints

## Route Summary

All endpoints are prefixed with `/api/` and require authentication unless noted.

## Error Response Format

All errors follow a consistent shape:
```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "errors": [
    {
      "field": "field_name",
      "message": "Field-specific error",
      "code": "INVALID"
    }
  ]
}
```

**Error Codes:**
- `UNAUTHENTICATED` - 401 (NotAuthenticated)
- `FORBIDDEN` - 403 (PermissionDenied)
- `VALIDATION_ERROR` - 400 (ValidationError)
- `RATE_LIMITED` - 429 (Throttled)
- `ERROR` - Other errors

## Rate Limiting

The following endpoints have rate limits:
- `POST /api/content/generate` - 10 requests/minute per user
- `POST /api/competitors/:id/recrawl` - 3 requests/minute per user
- `GET /api/jobs/:id/logs` - 60 requests/minute per user

When rate limited, returns 429 with `code: "RATE_LIMITED"`.

## Idempotency Keys

The following endpoints support idempotency keys:
- `POST /api/content/generate`
- `POST /api/templates/variants/:id/apply`

**Usage:**
Send an `Idempotency-Key` header (UUID) with your request. If the same key is used within 24 hours, the endpoint returns the same response without creating a new resource.

**Example:**
```bash
curl -X POST http://localhost:8000/api/content/generate \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 123e4567-e89b-12d3-a456-426614174000" \
  -H "Cookie: sessionid=..." \
  -d '{"brand_id": "...", "product_ids": [...], "fields": ["title"], "variants": 3}'
```

Repeating the same request with the same key returns the same `job_id` without creating a new job.

### Auth Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout  
- `GET /api/auth/me` - Get current user info

### Content Endpoints
- `POST /api/content/generate` - Generate content variants
- `POST /api/content/variants/bulk-accept` - Bulk accept variants
- `POST /api/content/variants/bulk-reject` - Bulk reject variants

### Competitor Endpoints
- `POST /api/competitors/:id/recrawl` - Trigger competitor recrawl

### Job Endpoints
- `GET /api/jobs/:id/logs?offset=0&limit=200` - Get job logs (paginated)

### Template Endpoints
- `POST /api/templates/variants/:id/apply` - Apply template variant to blueprint

### Brand Endpoints
- `GET /api/brands/:id/profile` - Get brand profile
- `PUT /api/brands/:id/profile` - Update brand profile
- `GET /api/brands/:id/blueprint` - Get blueprint
- `PUT /api/brands/:id/blueprint` - Update blueprint
- `POST /api/brands/:id/blueprint/sections` - Mutate blueprint sections

### Dashboard Endpoints
- `GET /api/dashboard/stats?brand_id=...` - Get dashboard statistics
- `GET /api/dashboard/activities?brand_id=...` - Get recent activities

---

## Example cURL Commands

### Auth

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@demo.com", "password": "password123!"}'
```
**Expected**: 200
```json
{
  "user": {"id": "...", "email": "admin@demo.com", ...},
  "roles": [...],
  "orgs": [...],
  "brands": [...]
}
```

**Me:**
```bash
curl http://localhost:8000/api/auth/me \
  -H "Cookie: sessionid=..."
```
**Expected**: 200

**Logout:**
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Cookie: sessionid=..."
```
**Expected**: 204

---

### Content Generation

```bash
curl -X POST http://localhost:8000/api/content/generate \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 123e4567-e89b-12d3-a456-426614174000" \
  -H "Cookie: sessionid=..." \
  -d '{
    "brand_id": "BRAND_ID",
    "product_ids": ["PROD_ID_1", "PROD_ID_2"],
    "fields": ["title", "description"],
    "variants": 3
  }'
```
**Expected**: 202
```json
{
  "job_id": "uuid-here"
}
```

**Validation errors:**
- `variants > 3` → 400 with `code: "VALIDATION_ERROR"`
- `product_ids` from wrong brand → 403 with `code: "FORBIDDEN"`
- Empty `fields` → 422 with `code: "VALIDATION_ERROR"`

**Idempotency:**
- Provide `Idempotency-Key` header (UUID) to prevent duplicate jobs
- Same key within 24h returns same `job_id` without creating new job

**Rate limit**: 10 requests/minute per user

---

### Competitor Recrawl

```bash
curl -X POST http://localhost:8000/api/competitors/COMPETITOR_ID/recrawl \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{
    "force": true,
    "max_pages": 10
  }'
```
**Expected**: 202
```json
{
  "crawl_run_id": "uuid-here",
  "job_id": "uuid-here"
}
```

**Caps:**
- Single SKU brand: max_pages capped at 5
- Multi SKU brand: max_pages capped at 10

**Rate limit**: 3 requests/minute per user

---

### Job Logs

```bash
curl "http://localhost:8000/api/jobs/JOB_ID/logs?offset=0&limit=200" \
  -H "Cookie: sessionid=..."
```
**Expected**: 200
```json
{
  "id": "job-uuid",
  "status": "success",
  "steps": [
    {
      "name": "validation",
      "status": "completed",
      "started_at": "2024-01-15T10:30:00Z",
      "finished_at": "2024-01-15T10:30:05Z",
      "lines": [
        {"ts": "2024-01-15T10:30:00Z", "level": "INFO", "msg": "Starting...", "idx": 0},
        {"ts": "2024-01-15T10:30:05Z", "level": "SUCCESS", "msg": "Done", "idx": 1}
      ]
    }
  ],
  "next_offset": 200
}
```

**Pagination:**
- Default `limit`: 200
- Max `limit`: 500 (capped)
- `next_offset` is present when more lines exist, `null` otherwise

**Cross-brand access**: Returns 404

**Rate limit**: 60 requests/minute per user

---

### Template Variant Apply

```bash
curl -X POST http://localhost:8000/api/templates/variants/VARIANT_ID/apply \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 123e4567-e89b-12d3-a456-426614174000" \
  -H "Cookie: sessionid=..."
```
**Expected**: 200
```json
{
  "blueprint_id": "uuid-here",
  "version": 2,
  "diff": {
    "tokens_changed": true,
    "sections_changed": true
  }
}
```

**Idempotency:**
- Provide `Idempotency-Key` header (UUID) to prevent duplicate blueprint versions
- Same key within 24h returns same `version` and `blueprint_id` without creating new version

---

### Brand Profile

**Get:**
```bash
curl http://localhost:8000/api/brands/BRAND_ID/profile \
  -H "Cookie: sessionid=..."
```
**Expected**: 200

**Update:**
```bash
curl -X PUT http://localhost:8000/api/brands/BRAND_ID/profile \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{
    "mission": "Updated mission",
    "single_sku": true
  }'
```
**Expected**: 200

**Competitor URL uniqueness**: Returns 400 if URL exists for another brand in same org

---

### Blueprint

**Get:**
```bash
curl http://localhost:8000/api/brands/BRAND_ID/blueprint \
  -H "Cookie: sessionid=..."
```
**Expected**: 200
```json
{
  "version": 1,
  "json": {
    "sections": [...]
  }
}
```

**Update:**
```bash
curl -X PUT http://localhost:8000/api/brands/BRAND_ID/blueprint \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{
    "json": {
      "sections": [...]
    }
  }'
```
**Expected**: 200 (version incremented)

**Sections Mutate:**
```bash
curl -X POST http://localhost:8000/api/brands/BRAND_ID/blueprint/sections \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{
    "action": "enable",
    "section_key": "hero",
    "index": 0
  }'
```
**Expected**: 200 (version incremented)

---

### Dashboard

**Stats:**
```bash
curl "http://localhost:8000/api/dashboard/stats?brand_id=BRAND_ID" \
  -H "Cookie: sessionid=..."
```
**Expected**: 200
```json
{
  "brand_id": "uuid-here",
  "counts": {
    "products": 10,
    "variants": 30,
    "accepted_variants": 15,
    "competitors": 3,
    "recent_jobs": 5
  },
  "jobs": {
    "pending": 1,
    "started": 0,
    "success": 10,
    "failure": 2
  }
}
```

**Activities:**
```bash
curl "http://localhost:8000/api/dashboard/activities?brand_id=BRAND_ID" \
  -H "Cookie: sessionid=..."
```
**Expected**: 200
```json
{
  "brand_id": "uuid-here",
  "activities": [
    {
      "id": "job-uuid",
      "type": "job",
      "task_name": "generate_content_task",
      "status": "success",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

### Bulk Variant Operations

**Bulk Accept:**
```bash
curl -X POST http://localhost:8000/api/content/variants/bulk-accept \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{
    "ids": ["VARIANT_ID_1", "VARIANT_ID_2"]
  }'
```
**Expected**: 200
```json
{
  "accepted": ["VARIANT_ID_1", "VARIANT_ID_2"],
  "failed": []
}
```

**Bulk Reject:**
```bash
curl -X POST http://localhost:8000/api/content/variants/bulk-reject \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{
    "ids": ["VARIANT_ID_1"]
  }'
```
**Expected**: 200
```json
{
  "rejected": ["VARIANT_ID_1"],
  "failed": []
}
```

---

## Test Results Summary

### Test Files Created
- `backend/tests/test_auth.py` - 5 tests
- `backend/tests/test_content_generate.py` - 4 tests
- `backend/tests/test_competitor_recrawl.py` - 3 tests
- `backend/tests/test_job_logs.py` - 3 tests
- `backend/tests/test_template_apply.py` - 2 tests
- `backend/tests/test_brand_profile.py` - 3 tests
- `backend/tests/test_blueprint.py` - 2 tests
- `backend/tests/test_dashboard.py` - 3 tests
- `backend/tests/test_bulk_variants.py` - 3 tests
- `backend/tests/test_idempotency.py` - 3 tests (NEW)
- `backend/tests/test_throttling.py` - 2 tests (NEW)
- `backend/tests/test_job_logs_pagination.py` - 3 tests (NEW)
- `backend/tests/test_error_shape.py` - 3 tests (NEW)

**Total**: 38 tests (28 original + 10 new)

### Test Execution
```bash
cd backend
pytest tests/ -v
```

---

## RBAC Rules

- **Auth required**: All endpoints except `/api/auth/login`
- **Brand scoped**: All endpoints with `brand_id` check brand ownership
- **Template/Blueprint mutations**: Require `BRAND_MANAGER` or `ORG_ADMIN` role
- **Content operations**: Require `EDITOR` or above

---

## Notes

- All endpoints use session authentication (Django default)
- `brand_id` can be provided in request body or via `X-Brand-ID` header
- Pagination: `limit` is capped at 500 for job logs (default: 200)
- Blueprint versioning: Always increments on PUT/POST
- Competitor URL uniqueness: Enforced at organization level
- CSRF: Same-site cookies configured for development; use CSRF token in curl or exempt endpoints
- Database indexes: Added for performance (`jobs.brand_id+created_at`, `content_variants.product_draft+status`)

## Demo CLI

Run end-to-end demo:
```bash
python manage.py demo_run_through --brand demo-brand-a
```

This command:
1. Checks competitor insights
2. Checks/generates blueprint
3. Generates content variants for 2 products (3 variants each)
4. Bulk accepts first variant for each product field
5. Mocks SEO generation
6. Applies template variant if available

Prints summary with job IDs, blueprint version, and counts.

---

## AI Framework Integration (Opt-in, Non-breaking)

**Note**: AI enhancements are available but **opt-in only** and **non-breaking**.

### Feature Flags

- `AI_FRAMEWORKS_ENABLED` - Default: `False` (must be explicitly enabled)
- `AI_SHADOW_MODE` - Default: `True` (run in background, don't affect responses)
- `AI_AUTOPILOT_ENABLED` - Default: `False` (fully opt-in)

### Behavior

**With defaults** (`AI_FRAMEWORKS_ENABLED=False`):
- All endpoints behave exactly as before
- No AI framework calls
- No breaking changes

**With shadow mode** (`AI_FRAMEWORKS_ENABLED=True`, `AI_SHADOW_MODE=True`):
- AI frameworks run in background (Celery tasks)
- FrameworkRun records are created for comparison
- **HTTP responses remain unchanged** (same as baseline)

**With active mode** (`AI_FRAMEWORKS_ENABLED=True`, `AI_SHADOW_MODE=False`):
- AI frameworks attempt to generate outputs
- If framework succeeds: outputs may be used (still matches existing response shapes)
- If framework fails: automatic fallback to existing logic with warning in logs

### Endpoints with AI Integration

- `POST /api/content/generate` - Optional AI product copy generation
- `PUT /api/brands/:id/blueprint` - Optional AI blueprint generation

**All existing response schemas are preserved.** AI enhancements are additive only.

### Shadow Mode Review

FrameworkRun records in Django admin show:
- Input hash (for deduplication)
- Baseline output (existing pipeline result)
- AI output (framework result)
- Diff summary (keys changed, length differences, lint results)

Use these to review AI performance before enabling active mode.

### How to Enable Shadow Mode in ST

1. Set environment variable: `AI_FRAMEWORKS_ENABLED=True`
2. Ensure `AI_SHADOW_MODE=True` (default)
3. Make requests to content/blueprint endpoints
4. Check Django admin `/admin/ai/frameworkrun/` to review FrameworkRun records
5. Compare baseline vs AI outputs in diff_summary

### Reviewing Diffs

FrameworkRun records include:
- `baseline_output` - Original pipeline result
- `output_data` - AI framework result
- `diff_summary.keys_changed` - List of fields that differ
- `diff_summary.length_diff` - Character length differences by field
- `diff_summary.lint_results` - Validation results (if applicable)

Use these to evaluate AI quality before disabling shadow mode.

### Shadow QA Report

**Command**:
```bash
python manage.py shadow_qa_report --brand demo-brand-a
```

**Output**:
- Framework status (SUCCESS/FAILED)
- Duration (ms)
- Keys changed count (should be 0 for shape)
- Length deltas by field
- Similarity results (max similarity, passed threshold)
- Lexicon results (forbidden/required terms)
- Top 3 diffs examples per framework

**Report Location**: `var/reports/shadow_qa_TIMESTAMP.json`

**Golden Tests**:
```bash
pytest backend/ai/tests/test_copy_golden.py -v
```

Tests verify:
- Schema validity and length policy
- No forbidden terms; required terms present
- Similarity below threshold (< 0.9)
- Golden baseline structure matches

**Golden Fixtures**: `backend/tests/fixtures/ai/golden_baseline.json`
- Generated on first run if missing
- Refresh by deleting and re-running test

---