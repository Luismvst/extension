# Project Cleanup Notes

## Files Moved to .trash/

This document tracks files that were moved to the `.trash/` directory during cleanup.

### Backend Cleanup
- `backend/app/utils/csv_logger.py` - Old CSV logger, replaced by `csv_ops_logger.py`
- `backend/app/core/unified_logger.py` - Old unified logger, replaced by `unified_order_logger.py`
- `backend/app/api/test.py` - Temporary test file created during debugging

### Temporary Files
- `backend-simple.py` - Temporary backend created for testing
- `fix_syntax_errors.py` - Temporary script for fixing syntax errors
- `fix_logger_calls.py` - Temporary script for fixing logger calls

### Test Files
- `test-backend/` - Obsolete test backend directory

### Build Artifacts
- `extension/out/` - Old build directory, replaced by `extension/dist/`

## Code Cleanup Actions

### Removed Commented Imports
Cleaned up commented import statements in adapter files:
- `backend/app/adapters/carriers/*.py`
- `backend/app/adapters/marketplaces/mirakl.py`
- `backend/app/api/carriers.py`
- `backend/app/api/marketplaces.py`
- `backend/app/core/webhook_service.py`

### Updated Documentation
- Updated function references in documentation
- Replaced old logger names with new implementations
- Ensured all examples use current APIs

## Verification Needed

The following items need manual review:
- Scripts in `scripts/` directory for potential consolidation
- Frontend components for unused files
- Extension files for optimization opportunities

## Current State

After cleanup, the project uses:
- `csv_ops_logger.py` for operations logging
- `unified_order_logger.py` for order state management
- Standardized CSV formats with proper headers
- Clean, uncommented import statements
