# Fetch History API Modularization Plan

## Goal
Move all fetch history API logic, models, and helpers out of `main.py` into dedicated modules for maintainability and clarity.

## Steps

1. **Create/Update Files**
   - `routes/fetch_history_routes.py`: For all fetch history API endpoints.
   - `models/fetch_history_models.py`: For all Pydantic models related to fetch history.
   - `utils/fetch_history_utils.py`: For any fetch history-specific helper functions.

2. **Move Code**
   - Move all `/api/fetch-history` endpoints from `main.py` to `routes/fetch_history_routes.py`.
   - Move all fetch history Pydantic models from `main.py` to `models/fetch_history_models.py`.
   - Move any fetch history-specific helpers to `utils/fetch_history_utils.py`.

3. **Update Imports**
   - In `routes/fetch_history_routes.py`, import models from `models/fetch_history_models.py`.
   - In `main.py`, import and include the router from `routes/fetch_history_routes.py`.

4. **Register Router**
   - In `main.py`, add:
     ```python
     from .routes import fetch_history_routes
     app.include_router(fetch_history_routes.router)
     ```

5. **Test**
   - Ensure all fetch history endpoints work as before.
   - Run backend tests and verify frontend integration.

## Notes

- Do not leave any fetch history logic in `main.py` except for router inclusion.
- If any code is shared with other modules, move it to a more general `utils/` file.
- Update documentation and references as needed.

---

**After this, repeat the process for other large feature areas (search, content fetch, etc.) for a fully modular backend.**