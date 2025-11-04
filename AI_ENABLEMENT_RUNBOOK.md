# AI Framework Enablement Runbook

One-page guide to operate the AI layer safely without keys, and to enable frameworks live later with minimal risk.

---

## 1) Environments and Defaults

**ST (sandbox/testing)**: AI on in shadow, mock outputs only.

**UAT/PROD**: AI off by default; shadow allowed, no external calls until keys provided.

### Recommended .env Values

**ST (.env.st)**
```bash
AI_FRAMEWORKS_ENABLED=true
AI_SHADOW_MODE=true
AI_FRAMEWORKS_ENABLED_BY_NAME={}
AI_SHADOW_MODE_BY_NAME={}
AI_PROVIDER=abacus
AI_USE_MOCK_BY_FRAMEWORK={"product_copy": true, "seo": true, "blueprint": true}
USE_MOCK_LLM=true
ROUTELLM_API_KEY= (leave empty)
```

**UAT (.env.uat)**
```bash
AI_FRAMEWORKS_ENABLED=false
AI_SHADOW_MODE=true
AI_USE_MOCK_BY_FRAMEWORK={}
ROUTELLM_API_KEY= (leave empty)
```

**PROD (.env.prod)**
```bash
AI_FRAMEWORKS_ENABLED=false
AI_SHADOW_MODE=true
AI_USE_MOCK_BY_FRAMEWORK={}
ROUTELLM_API_KEY= (leave empty; set in secrets manager)
```

### Startup Safety

- **With empty `ROUTELLM_API_KEY`**: AbacusProvider forces mock mode and never performs network calls.
- **Startup logs** at boot (one line per framework) showing: enabled, shadow, mock, provider.

---

## 2) Daily Operations (No API Keys)

### Shadow Runs with Mocks

**Seed and run:**
```bash
python manage.py seed_demo_data
python manage.py shadow_qa_report --brand demo-brand-a
```

**Review report** at `var/reports/shadow_qa_TIMESTAMP.json`:
- `schema_valid: true`
- `lexicon`: no forbidden terms; required terms respected
- `similarity flags`: 0 or low
- `durations`: low; `cache_hit_rate` improves on second run

### Golden Tests and Validators

```bash
pytest backend/ai/tests/test_copy_golden.py -v
pytest backend/ai/tests/test_validators_similarity.py -v
```

### Cache and Telemetry Checks

1. Trigger SEO generate twice for same inputs.
2. Verify FrameworkRun entries show `cached=true` and `duration_ms ~0` on the second call.

### Admin/Internal Telemetry (if implemented)

```bash
GET /api/internal/ai/telemetry?days=7 (admin-only)
```

Check runs, cache hit rate, median duration.

---

## 3) Adding Keys Later (Abacus Live)

### Where to Store Keys

- Set `ROUTELLM_API_KEY` in the environment or your secrets manager.
- **Never commit keys** to code or `.env` examples.

### Safe Rollout Plan (ST First, One Framework at a Time)

**Step 1: Keep shadow mode; turn off mocks for SEO only:**
```bash
AI_FRAMEWORKS_ENABLED_BY_NAME={"seo": true}
AI_SHADOW_MODE_BY_NAME={"seo": true}
AI_USE_MOCK_BY_FRAMEWORK={"seo": false}
ROUTELLM_API_KEY=your_real_key
```

**Run:**
```bash
python manage.py shadow_qa_report --brand demo-brand-a
```

**Verify FrameworkRun**: `used_mock=false`, `model_name` set, durations acceptable.

**Step 2: Switch SEO to live (non-shadow) in ST:**
```bash
AI_SHADOW_MODE_BY_NAME={"seo": false}
```

**Validate**: Endpoint responses (shape unchanged) and latency.

**Step 3: UAT rollout for SEO:**
- Enable SEO for one brand; keep product_copy/blueprint in shadow.
- Gather editor feedback; monitor lints and acceptance rate.

### Guardrails Before Enabling More

- ✅ Throttles and quotas configured (you already added them).
- ✅ Caching working (input_hash stable; cache hit rate >50% on repeats).
- ✅ Telemetry reviewed daily for anomalies (errors, durations).

---

## 4) Operating Modes and Toggles (Per Framework)

**Enable/disable framework:**
```bash
AI_FRAMEWORKS_ENABLED_BY_NAME={"product_copy": true}
```

**Shadow vs live:**
```bash
AI_SHADOW_MODE_BY_NAME={"product_copy": true|false}
```

**Mock vs real:**
```bash
AI_USE_MOCK_BY_FRAMEWORK={"product_copy": true|false}
```

**Global fallbacks:**
- If per-framework maps omit a framework, global flags apply.

**Hard safety:**
- If `ROUTELLM_API_KEY` is empty, provider remains mock regardless of flags.

---

## 5) Quick Verification Commands

**Health:**
```bash
curl http://localhost:8000/api/health
```

**Shadow QA:**
```bash
python manage.py shadow_qa_report --brand demo-brand-a
```

**Tests:**
```bash
pytest backend/ai/tests -v
```

**Telemetry (admin-only):**
```bash
curl -H "Authorization: Bearer TOKEN" "http://localhost:8000/api/internal/ai/telemetry?days=7"
```

---

## 6) Autopilot and Site Changes (Keep Disabled by Default)

**Defaults in BrandAIConfig:**
- `control_mode="manual"`
- `autopilot_risk_max="low"`
- `autopilot_daily_cap=10`

**Keep `AI_AUTOPILOT_ENABLED=false` until:**
- SEO live is stable in UAT.
- ChangeSets are limited to low-risk ops (meta/alt/heading normalization).

**When testing Autopilot in ST:**
- Enable per test brand only.
- Verify apply/revert and audit logs.

---

## 7) Troubleshooting Checklist

**Unexpected network calls:**
- ✅ Ensure `ROUTELLM_API_KEY` is empty; check startup logs for "MOCK mode."
- ✅ Confirm `AI_USE_MOCK_BY_FRAMEWORK` sets true.

**No FrameworkRun entries in shadow:**
- ✅ Verify `AI_FRAMEWORKS_ENABLED=true` and `AI_SHADOW_MODE=true` for that framework.

**Cache not hitting:**
- ✅ Ensure inputs/policy_version identical; check input_hash in FrameworkRun.

**429s from throttles:**
- ✅ You can temporarily raise limits in ST; keep PROD strict.

---

## 8) Future-Proofing for Your Own AI

**Keep `AI_PROVIDER="abacus"` now.**

**To validate the adapter boundary later:**
- Set `AI_PROVIDER="local"`
- Ensure outputs pass validators and endpoint shapes remain identical.
- **Do not enable LocalProvider in UAT/PROD**; use only for dev benchmarking.

---

## Startup Logs Example

When Django starts, you'll see:
```
============================================================
AI Framework Status (Startup)
============================================================
Provider: abacus
API Key Present: False
  → MOCK mode enforced (no API key)
------------------------------------------------------------
✗ [AI] Framework product_copy: enabled=False, shadow=True, mock=True, provider=abacus
✗ [AI] Framework seo: enabled=False, shadow=True, mock=True, provider=abacus
✗ [AI] Framework blueprint: enabled=False, shadow=True, mock=True, provider=abacus
============================================================
```

---

**Last Updated**: 2024-01-15  
**Status**: Ready for ST shadow mode testing

