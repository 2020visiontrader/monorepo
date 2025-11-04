# API Requirements Document

## 📋 Current API Status

### ✅ **Implemented APIs**

#### **Core APIs**
- `GET /api/organizations/` - List organizations
- `GET /api/organizations/:id` - Get organization
- `GET /api/users/` - List users
- `GET /api/jobs/:id/status` - Get job status

#### **Brands APIs**
- `GET /api/brands/` - List brands
- `GET /api/brands/:id` - Get brand
- `POST /api/brands/` - Create brand
- `PUT /api/brands/:id` - Update brand
- `DELETE /api/brands/:id` - Delete brand
- `POST /api/brands/:id/onboarding` - Save brand profile
- `POST /api/brands/:id/blueprint/generate` - Generate site blueprint
- `GET /api/brands/:id/pathways/` - List pathways
- `POST /api/brands/:id/pathways/` - Create pathway
- `GET /api/brands/:id/pathways/:id` - Get pathway
- `PUT /api/brands/:id/pathways/:id` - Update pathway

#### **Competitors APIs**
- `GET /api/competitors/` - List competitors
- `GET /api/competitors/:id` - Get competitor
- `POST /api/competitors/` - Create competitor
- `POST /api/competitors/ingest` - Ingest competitor URLs
- `GET /api/competitors/insights` - Get competitor insights
- `POST /api/competitors/:id/recrawl` - **MISSING** - Trigger recrawl

#### **Content APIs**
- `GET /api/content/products/` - List product drafts
- `GET /api/content/products/:id` - Get product draft
- `POST /api/content/products/` - Create product draft
- `GET /api/content/variants/` - List content variants
- `GET /api/content/variants/:id` - Get variant
- `POST /api/content/variants/:id/accept` - Accept variant
- `POST /api/content/variants/:id/reject` - Reject variant
- `POST /api/content/generate` - **MISSING** - Generate content (needs endpoint)
- `POST /api/content/publish` - Publish to Shopify
- `GET /api/content/publish/` - List publish jobs
- `GET /api/content/publish/:id` - Get publish job

#### **SEO APIs**
- `GET /api/seo/plans/` - List SEO plans
- `GET /api/seo/plans/:id` - Get SEO plan
- `POST /api/seo/generate` - Generate SEO optimization
- `GET /api/seo/keywords/` - **MISSING** - List keyword seeds

#### **Frameworks APIs**
- `GET /api/frameworks/` - List frameworks
- `GET /api/frameworks/:id` - Get framework
- `POST /api/frameworks/ingest` - Ingest framework candidate
- `GET /api/frameworks/candidates/` - List candidates
- `POST /api/frameworks/candidates/:id/approve` - Approve candidate

#### **Shopify APIs**
- `GET /api/shopify/oauth/install` - Initiate OAuth
- `GET /api/shopify/oauth/callback` - Handle OAuth callback
- `GET /api/shopify/connection` - **MISSING** - Get connection status
- `POST /api/shopify/disconnect` - **MISSING** - Disconnect store

#### **Templates APIs**
- `GET /api/templates/` - List templates
- `GET /api/templates/:id` - Get template
- `POST /api/templates/generate` - Generate template
- `POST /api/templates/upload` - Upload template
- `GET /api/templates/variants/` - List variants
- `POST /api/templates/variants/` - Create variant
- `GET /api/templates/variants/:id` - Get variant
- `PUT /api/templates/variants/:id` - Update variant
- `POST /api/templates/variants/:id/apply` - **MISSING** - Apply to Site Blueprint

---

## ❌ **Missing APIs (Required for Frontend)**

### **1. Authentication & Session**
```
POST /api/auth/login          - User login
POST /api/auth/logout         - User logout
GET  /api/auth/me             - Get current user
POST /api/auth/refresh        - Refresh session
```

### **2. Brand Profile**
```
GET  /api/brands/:id/profile  - Get brand profile
PUT  /api/brands/:id/profile  - Update brand profile
```

### **3. Content Generation**
```
POST /api/content/generate    - Generate content variants
  Body: {
    brand_id: UUID,
    product_ids: [UUID],
    fields: ['title', 'description', 'bullets'],
    max_variants: 3
  }
```

### **4. Competitor Management**
```
POST /api/competitors/:id/recrawl    - Trigger recrawl
GET  /api/competitors/:id/pages      - Get crawled pages
GET  /api/competitors/:id/ia         - Get IA signature
```

### **5. SEO Management**
```
GET  /api/seo/keywords/              - List keyword seeds
POST /api/seo/keywords/               - Add keyword seeds
GET  /api/seo/plans/:id/clusters      - Get keyword clusters
PUT  /api/seo/plans/:id               - Update SEO plan
```

### **6. Shopify Integration**
```
GET  /api/shopify/connection         - Get connection status
POST /api/shopify/disconnect         - Disconnect store
GET  /api/shopify/products            - List Shopify products
GET  /api/shopify/products/:id        - Get Shopify product
POST /api/shopify/sync                - Sync products from Shopify
```

### **7. Template Operations**
```
POST /api/templates/variants/:id/apply - Apply variant to Site Blueprint
GET  /api/templates/:id/sections       - Get template sections
PUT  /api/templates/:id/sections      - Update section order
```

### **8. Site Blueprint**
```
GET  /api/brands/:id/blueprint        - Get current blueprint
PUT  /api/brands/:id/blueprint        - Update blueprint
POST /api/brands/:id/blueprint/sections - Update sections
```

### **9. Jobs & Monitoring**
```
GET  /api/jobs/                       - List all jobs
GET  /api/jobs/:id/logs               - Get job logs
POST /api/jobs/:id/retry              - Retry failed job
DELETE /api/jobs/:id                  - Cancel job
```

### **10. Dashboard & Analytics**
```
GET  /api/dashboard/stats             - Get dashboard statistics
GET  /api/dashboard/activities         - Get recent activities
GET  /api/analytics/content           - Content analytics
GET  /api/analytics/seo                - SEO analytics
```

---

## 🔧 **API Improvements Needed**

### **1. Pagination**
All list endpoints should support:
- `?page=1&page_size=20`
- Response includes `count`, `next`, `previous`

### **2. Filtering & Search**
- `?search=query` - Search across relevant fields
- `?filter=field:value` - Filter by fields
- `?ordering=field` - Order results

### **3. Bulk Operations**
```
POST /api/content/variants/bulk-accept  - Accept multiple variants
POST /api/content/variants/bulk-reject  - Reject multiple variants
POST /api/seo/bulk-publish              - Bulk publish SEO changes
```

### **4. File Upload**
```
POST /api/templates/upload              - Upload template file (multipart/form-data)
POST /api/brands/:id/logo                - Upload brand logo
POST /api/products/:id/images            - Upload product images
```

### **5. Export/Import**
```
GET  /api/brands/:id/export              - Export brand data
POST /api/brands/:id/import              - Import brand data
GET  /api/seo/plans/:id/export           - Export SEO plan
```

### **6. Webhooks (Future)**
```
POST /api/webhooks/shopify              - Shopify webhook handler
POST /api/webhooks/llm                  - LLM completion webhook
```

---

## 📝 **Request/Response Examples**

### **Content Generation**
```http
POST /api/content/generate
Content-Type: application/json
X-Brand-ID: <brand-id>

{
  "product_ids": ["uuid1", "uuid2"],
  "fields": ["title", "description", "bullets"],
  "max_variants": 3,
  "framework_id": "uuid"
}

Response:
{
  "task_id": "uuid",
  "status": "pending",
  "estimated_time": "2m"
}
```

### **SEO Generate**
```http
POST /api/seo/generate
Content-Type: application/json
X-Brand-ID: <brand-id>

{
  "scope": "all",
  "items": [
    {"id": "uuid1", "type": "product"},
    {"id": "uuid2", "type": "page"}
  ]
}

Response:
{
  "task_id": "uuid",
  "status": "pending"
}
```

### **Template Generate**
```http
POST /api/templates/generate
Content-Type: application/json

{
  "complexity": "Sophisticated",
  "industry": "Fashion",
  "brand_tone": {
    "professional": 0.8,
    "friendly": 0.7
  },
  "competitor_refs": ["url1", "url2"]
}

Response:
{
  "id": "uuid",
  "name": "Sophisticated Fashion Template",
  "manifest": {...}
}
```

### **Template Upload**
```http
POST /api/templates/upload
Content-Type: multipart/form-data

{
  "file": <File>,
  "validate": true
}

Response:
{
  "id": "uuid",
  "name": "Uploaded Template",
  "validation_errors": [],
  "manifest": {...}
}
```

---

## 🎯 **Priority Implementation Order**

### **Phase 1: Critical (Needed Now)**
1. ✅ Authentication endpoints
2. ✅ Content generation endpoint
3. ✅ Competitor recrawl endpoint
4. ✅ Job logs endpoint
5. ✅ Shopify connection status

### **Phase 2: Important (Soon)**
6. ✅ Bulk operations
7. ✅ File upload handling
8. ✅ Dashboard stats
9. ✅ Blueprint management
10. ✅ Template variant apply

### **Phase 3: Nice to Have**
11. ✅ Export/Import
12. ✅ Advanced filtering
13. ✅ Analytics endpoints
14. ✅ Webhooks

---

## 🔐 **Authentication Requirements**

All endpoints (except auth) require:
- `X-Organization-ID` header (for multi-tenancy)
- `X-Brand-ID` header (for brand-scoped endpoints)
- Session authentication or JWT token

### **Example Headers**
```
X-Organization-ID: <org-uuid>
X-Brand-ID: <brand-uuid>
Authorization: Bearer <token>
Cookie: sessionid=<session-id>
```

---

## 📊 **Response Format Standards**

### **Success Response**
```json
{
  "data": {...},
  "meta": {
    "count": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### **Error Response**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Field validation failed",
    "details": {
      "mission": ["This field is required"]
    }
  }
}
```

### **Job/Task Response**
```json
{
  "task_id": "uuid",
  "status": "pending|running|completed|failed",
  "result": {...},
  "error": null
}
```

---

## 🧪 **Testing Requirements**

Each API endpoint needs:
- Unit tests for validation
- Integration tests with fixtures
- Permission tests (RBAC)
- Error handling tests
- Rate limiting tests (where applicable)

---

## 📈 **Performance Considerations**

- **Pagination:** All list endpoints max 100 items per page
- **Timeout:** 30s for long-running operations
- **Rate Limiting:** 100 requests/minute per user
- **Caching:** GET endpoints cached for 5 minutes
- **Background Jobs:** Operations > 5s should be async

---

## 🔄 **API Versioning**

Current: `v1` (implicit)
Future: `/api/v2/...` when breaking changes needed

---

## 📚 **Documentation Needs**

- OpenAPI/Swagger spec
- Postman collection
- API usage examples
- Error code reference
- Rate limit documentation

