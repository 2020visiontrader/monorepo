# ST Testing Environment Status

## Environment: ST (Staging/Testing)

**Status:** ✅ All services running and ready for manual testing

## Services Status

| Service | Status | Port | Health |
|---------|--------|------|--------|
| Backend API | ✅ Running | 8000 | Healthy |
| Frontend | ✅ Running | 3000 | Healthy |
| PostgreSQL | ✅ Running | 5432 | Healthy |
| Redis | ✅ Running | 6379 | Healthy |
| Celery Worker | ✅ Running | - | Healthy |

## Access URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **API Docs:** http://localhost:8000/api/ (if available)

## Demo Credentials

- **Email:** admin@demo.com
- **Password:** password123!
- **Role:** ORG_ADMIN

## Seeded Data

- **Organizations:** 1
  - Demo Agency (slug: demo-agency)
- **Users:** 1
  - admin@demo.com (admin)
- **Brands:** 2
  - Demo Brand A (slug: demo-brand-a)
  - Demo Brand B (slug: demo-brand-b)

## Environment Configuration

- **ENVIRONMENT:** ST
- **DEBUG:** True
- **AI Mode:** MOCK (no API key - safe for testing)
- **Database:** PostgreSQL (ecommerce_optimizer)
- **Cache/Broker:** Redis

## Worker Tasks Available

- `ai.tasks.shadow_run_blueprint`
- `ai.tasks.shadow_run_product_copy`
- `ai.tasks.shadow_run_seo`
- `competitors.tasks.crawl_competitor_task`
- `content.tasks.generate_content_task`
- `content.tasks.publish_to_shopify_task`
- `seo.tasks.generate_seo_task`

## Quick Commands

```bash
# Check service status
cd ops && docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend
docker-compose restart worker

# Stop all services
docker-compose down

# Start all services
docker-compose up -d
```

## Next Steps for Manual Testing

1. Access the frontend at http://localhost:3000
2. Log in with admin@demo.com / password123!
3. Test API endpoints via http://localhost:8000/api/
4. Access admin panel at http://localhost:8000/admin
5. Test AI frameworks (running in shadow/mock mode)
6. Test content generation, SEO, and blueprint features

## Notes

- All AI frameworks are running in MOCK mode (no external API calls)
- Shadow mode is enabled for safe testing
- Database migrations are up to date
- Demo data is seeded and ready for testing
