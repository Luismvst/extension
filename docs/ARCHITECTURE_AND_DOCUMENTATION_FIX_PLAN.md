# Architecture and Documentation Fix Plan

## Executive Summary

This document outlines all inconsistencies found between documentation and implementation, and provides a systematic plan to resolve them.

## Issues Identified

### 1. Unmounted Routers
**Problem:** Three routers are defined but not mounted in `main.py`:
- `map_router.py` - TIPSA mapping endpoints
- `ship_router.py` - Carrier shipment stubs
- `tracking_router.py` - Tracking update stubs

**Impact:** These endpoints are defined but completely inaccessible.

**Decision Required:**
- **Option A:** Mount them with proper prefixes
  - `/api/v1/map/*` for map_router
  - `/api/v1/ship/*` for ship_router
  - `/api/v1/tracking/*` for tracking_router
- **Option B:** Remove them if not needed for MVP
- **Recommendation:** Remove them since their functionality is already covered by:
  - Map functionality: In the extension (client-side mapping)
  - Ship functionality: In `/api/v1/carriers/{carrier}/shipments`
  - Tracking functionality: In `/api/v1/orchestrator/push-tracking-to-mirakl`

### 2. Health Endpoint Documentation Inconsistencies

**Problem:** Documentation references non-existent health check endpoints:
- RUNBOOK.md mentions `/api/v1/health/mirakl` and `/api/v1/health/tipsa`
- ARCHITECTURE.md references `GET /health` (without `/api/v1` prefix)

**Reality:** Only these endpoints exist:
- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health check

**Fix:** Update all documentation to reflect actual endpoints.

### 3. Debug Print Statements

**Problem:** `orchestrator.py` contains numerous debug print statements:
- Lines 372-388: Individual order logging debug
- Lines 392-412: csv_ops_logger debugging

**Fix:** Remove all print statements and use structured logging instead.

### 4. Documentation Language Inconsistency

**Problem:** Mixed Spanish/English in documentation:
- ARCHITECTURE.md is in Spanish
- ENDPOINTS.md, FLOWS.md, LOGGING.md are in English
- Code comments are mostly in English

**Fix:** Standardize all documentation to English (code language).

### 5. API Route Prefix Inconsistency

**Problem:** ARCHITECTURE.md shows examples without `/api/v1` prefix:
- `POST /map/tipsa` (should be `/api/v1/map/tipsa` if mounted)
- `GET /health` (should be `/api/v1/health/`)

**Fix:** Update all examples to include proper prefixes.

## Detailed Fix Plan

### Phase 1: Clean Up Unused Code ✅

1. **Remove unmounted routers** (or document them as "future enhancements"):
   - Delete or mark as deprecated: `map_router.py`, `ship_router.py`, `tracking_router.py`
   - Add note in ARCHITECTURE.md explaining why they're not needed

2. **Remove debug prints from orchestrator.py**:
   - Lines 372-388: Remove print statements for individual order logging
   - Lines 392-412: Remove csv_ops_logger debug prints
   - Replace with proper `logger.debug()` calls if needed

### Phase 2: Update Documentation ✅

1. **Update ARCHITECTURE.md**:
   - Translate to English or keep Spanish but mark it clearly
   - Fix all API endpoint examples to include `/api/v1` prefix
   - Remove references to unmounted routers
   - Update diagram to show actual endpoints

2. **Update RUNBOOK.md**:
   - Remove examples for `/api/v1/health/mirakl` and `/api/v1/health/tipsa`
   - Add examples for `/api/v1/health/` and `/api/v1/health/detailed`
   - Verify all curl examples use correct endpoints

3. **Verify ENDPOINTS.md**:
   - Check that all documented endpoints actually exist in code
   - Remove any references to unmounted routers
   - Ensure all examples are accurate

4. **Verify FLOWS.md and LOGGING.md**:
   - Check for accuracy
   - Update any incorrect endpoint references

### Phase 3: Data Model Synchronization ✅

1. **Review Pydantic models** (backend/app/models/order.py):
   - Document all fields clearly
   - Ensure consistency with unified_order_logger CSV headers

2. **Review Zod schemas** (extension):
   - Ensure they match Pydantic models
   - Document any intentional differences

3. **Field mapping**:
   - Create a mapping table showing backend ↔ frontend field names
   - Document in a new file: `docs/DATA_MODELS.md`

### Phase 4: Create Testing Plan ✅

Create `docs/TESTING_PLAN.md` with:
1. **Unit Tests** - For each service/adapter
2. **Integration Tests** - For each API endpoint
3. **E2E Tests** - For complete workflows
4. **Manual Testing Checklist** - Based on VALIDATION_CHECKLIST.md

### Phase 5: Implement Fixes

Execute all fixes in order:
1. Code cleanup
2. Documentation updates
3. Testing

## Actual Endpoints (Reference)

### Mounted Routers

```python
# From backend/app/main.py
app.include_router(health.router)        # /api/v1/health
app.include_router(auth.router)          # /auth
app.include_router(marketplaces.router)  # /api/v1/marketplaces
app.include_router(carriers.router)      # /api/v1/carriers
app.include_router(orchestrator.router)  # /api/v1/orchestrator
app.include_router(logs.router)          # /api/v1/logs
app.include_router(orders.router)        # /api/v1/orders
```

### NOT Mounted (Currently Unused)
- `map_router.py` - Would be `/api/v1/map/*` if mounted
- `ship_router.py` - Would be `/api/v1/ship/*` if mounted
- `tracking_router.py` - Would be `/api/v1/tracking/*` if mounted

## Summary of Changes

| File | Change Type | Description |
|------|------------|-------------|
| `backend/app/api/map_router.py` | DELETE or DEPRECATE | Not mounted, functionality covered elsewhere |
| `backend/app/api/ship_router.py` | DELETE or DEPRECATE | Not mounted, functionality in carriers router |
| `backend/app/api/tracking_router.py` | DELETE or DEPRECATE | Not mounted, functionality in orchestrator |
| `backend/app/api/orchestrator.py` | CLEAN | Remove debug print statements |
| `docs/ARCHITECTURE.md` | UPDATE | Fix endpoint examples, remove unmounted router refs |
| `docs/RUNBOOK.md` | UPDATE | Fix health check examples |
| `docs/ENDPOINTS.md` | VERIFY | Ensure all endpoints are accurate |
| `docs/DATA_MODELS.md` | CREATE | Document field mappings |
| `docs/TESTING_PLAN.md` | CREATE | Comprehensive testing strategy |

## Timeline

- **Phase 1:** 1 hour (code cleanup)
- **Phase 2:** 2 hours (documentation updates)
- **Phase 3:** 1 hour (data model review)
- **Phase 4:** 1 hour (testing plan creation)
- **Phase 5:** 1 hour (implementation and verification)

**Total Estimated Time:** 6 hours

## Success Criteria

- ✅ No unmounted routers or dead code
- ✅ All documentation examples work as written
- ✅ Consistent English language in docs
- ✅ All API routes properly prefixed
- ✅ No debug print statements in production code
- ✅ Data models documented and synchronized
- ✅ Comprehensive testing plan in place

