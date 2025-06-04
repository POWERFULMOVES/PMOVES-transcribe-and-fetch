from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path
from typing import List, Union, Dict, Any, Optional # Added Dict, Any, Optional
from uuid import UUID, uuid4 # Added uuid4
import logging
from datetime import datetime, timezone # Added timezone

# Assuming Supabase client is available via a dependency, e.g., get_supabase_client
# from ..dependencies import get_supabase_client # Adjust import as per project structure
# For now, mock or assume direct Supabase usage if dependency is not clear.
# from supabase_py_async import AsyncClient  # Example if using supabase-py-async directly

# Import Pydantic models
from ..models.presets_models import CrawlPresetCreate, CrawlPresetUpdate, CrawlPresetResponse

# Placeholder for Supabase client dependency
# This will need to be adapted to how Supabase is integrated in the actual project
# For the subtask, we'll write the logic assuming a 'supabase_client' object exists.

# A mock Supabase client for subtask execution if a real one isn't injectable
class MockSupabaseDBResponse:
    def __init__(self, data: Optional[List[Dict[str, Any]]] = None, error: Optional[Any] = None, count: Optional[int] = None):
        self.data = data if data is not None else []
        self.error = error
        self.count = count

class MockSupabaseQueryBuilder:
    def __init__(self, client: Any, table_name: str):
        self._client = client
        self._table_name = table_name
        self._select_columns: Optional[str] = None
        self._filters: List[tuple] = []
        self._insert_data: Optional[dict] = None
        self._update_data: Optional[dict] = None
        self._limit_count: Optional[int] = None
        self._offset_count: Optional[int] = None
        self._or_conditions: Optional[str] = None


    async def insert(self, data: Union[List[Dict[str, Any]], Dict[str, Any]], returning: str = "representation"): # Adjusted to match supabase-py v1 type hints
        self._insert_data = data[0] if isinstance(data, list) else data # Supabase typically takes a list
        logger.info(f"MOCK DB INSERT into {self._table_name}: {self._insert_data}")
        # Simulate database behavior
        if not self._insert_data.get('preset_id'): self._insert_data['preset_id'] = uuid4()
        self._insert_data['created_at'] = datetime.now(timezone.utc)
        self._insert_data['updated_at'] = datetime.now(timezone.utc)
        # created_by should be set by application logic using auth.uid()
        return MockSupabaseDBResponse(data=[self._insert_data])

    async def select(self, columns: str = "*"):
        self._select_columns = columns
        return self

    async def eq(self, column: str, value: Any):
        self._filters.append(('eq', column, value))
        return self

    async def or_(self, or_conditions: str): # Simplified for mock
        self._or_conditions = or_conditions
        return self

    async def limit(self, count: int):
        self._limit_count = count
        return self

    async def offset(self, count: int): # Added offset for pagination
        self._offset_count = count
        return self

    async def update(self, data: Dict[str, Any]):
        self._update_data = data
        logger.info(f"MOCK DB UPDATE {self._table_name} with data {self._update_data} and filters: {self._filters}")
        # Simulate returning updated data, RLS would restrict this in reality
        updated_item = {'preset_id': self._filters[0][2] if self._filters else uuid4(), **self._update_data} # Assuming filter is on preset_id
        updated_item['updated_at'] = datetime.now(timezone.utc)
        # Ensure all fields for CrawlPresetResponse are present if possible
        updated_item.setdefault('preset_name', 'Updated Preset Name')
        updated_item.setdefault('strategy_definition', {})
        updated_item.setdefault('created_at', datetime.now(timezone.utc) - timezone.utc.dst()) # Example past time
        return MockSupabaseDBResponse(data=[updated_item])


    async def delete(self):
        logger.info(f"MOCK DB DELETE from {self._table_name} with filters: {self._filters}")
        # Supabase delete returns the deleted records
        if self._filters: # Simulate a record was found and deleted
             return MockSupabaseDBResponse(data=[{'preset_id': self._filters[0][2]}]) # Assuming filter is on preset_id
        return MockSupabaseDBResponse(data=[])


    async def execute(self) -> MockSupabaseDBResponse: # Common execute method
        logger.info(f"MOCK DB EXECUTE on {self._table_name} with filters: {self._filters}, select: {self._select_columns}, or: {self._or_conditions}, limit: {self._limit_count}, offset: {self._offset_count}")
        # This mock execute needs to handle different operations based on what was called before
        if self._insert_data: # Should have been handled by .insert() itself for this mock
            return MockSupabaseDBResponse(data=[self._insert_data])
        if self._update_data: # Should have been handled by .update()
             updated_item = {'preset_id': self._filters[0][2] if self._filters else uuid4(), **self._update_data}
             return MockSupabaseDBResponse(data=[updated_item])
        if self._select_columns: # Handle select
            # Simplified: if filtering by a UUID preset_id or a name, return a mock item
            if any(f[0] == 'eq' and f[1] == 'preset_id' for f in self._filters) or \
               any(f[0] == 'eq' and f[1] == 'preset_name' for f in self._filters):
                # Try to get the ID/name from the filter for more realistic mock
                identifier_val = None
                for f_type, f_col, f_val in self._filters:
                    if f_col in ['preset_id', 'preset_name']:
                        identifier_val = f_val
                        break
                mock_item = {
                    'preset_id': identifier_val if isinstance(identifier_val, UUID) else uuid4(),
                    'preset_name': identifier_val if isinstance(identifier_val, str) else 'Test Preset from DB',
                    'description': 'A test preset description',
                    'version': 1,
                    'crawl_tool': 'crawl4ai',
                    'strategy_definition': {"strategy": "ExampleStrategy"},
                    'target_capability': 'web_research',
                    'tags': ['test', 'example'],
                    'created_by': uuid4(),
                    'created_at': datetime.now(timezone.utc),
                    'updated_at': datetime.now(timezone.utc)
                }
                return MockSupabaseDBResponse(data=[mock_item])
            # Default for list presets (no specific filter or other filters)
            return MockSupabaseDBResponse(data=[
                {'preset_id': uuid4(), 'preset_name': 'Preset 1', 'description': 'Desc 1', 'version': 1, 'crawl_tool': 'crawl4ai', 'strategy_definition': {}, 'target_capability': 'data_extraction', 'tags':['tag1'], 'created_by': uuid4(), 'created_at': datetime.now(timezone.utc) , 'updated_at': datetime.now(timezone.utc)},
                {'preset_id': uuid4(), 'preset_name': 'Preset 2', 'description': 'Desc 2', 'version': 2, 'crawl_tool': 'crawl4ai', 'strategy_definition': {}, 'target_capability': 'web_research', 'tags':['tag2'], 'created_by': uuid4(), 'created_at': datetime.now(timezone.utc) , 'updated_at': datetime.now(timezone.utc)}
            ])
        # Fallback for delete or other operations not returning data explicitly in mock
        return MockSupabaseDBResponse(data=[])


class MockSupabaseClient:
    def table(self, table_name: str) -> MockSupabaseQueryBuilder:
        return MockSupabaseQueryBuilder(self, table_name)

supabase_client = MockSupabaseClient()

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/presets", tags=["Crawl Presets"])

@router.post("", response_model=CrawlPresetResponse, status_code=201)
async def create_crawl_preset(preset_data: CrawlPresetCreate = Body(...)):
    # In a real app, created_by would be set from authenticated user's ID.
    # For Supabase RLS to work on insert, the user must be authenticated.
    # The 'created_by' field would typically be set by a trigger or application logic.
    # preset_dict = preset_data.model_dump()
    # preset_dict["created_by"] = current_user_id  # This needs actual auth integration

    response = await supabase_client.table("crawl_presets").insert(preset_data.model_dump()).execute() # Supabase insert expects a list

    if response.error:
        logger.error(f"Error creating preset: {response.error}")
        # Attempt to access error details more safely
        error_detail = "Database error during preset creation."
        if hasattr(response.error, 'message') and response.error.message:
            error_detail = str(response.error.message)
        elif isinstance(response.error, dict) and response.error.get('message'):
            error_detail = response.error.get('message')
        raise HTTPException(status_code=400, detail=error_detail)
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create preset, no data returned.")
    return CrawlPresetResponse(**response.data[0])

@router.get("", response_model=List[CrawlPresetResponse])
async def list_crawl_presets(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    response = await supabase_client.table("crawl_presets").select("*").offset(skip).limit(limit).execute()
    if response.error:
        logger.error(f"Error listing presets: {response.error}")
        error_detail = "Database error listing presets."
        if hasattr(response.error, 'message') and response.error.message: error_detail = str(response.error.message)
        raise HTTPException(status_code=500, detail=error_detail)
    return [CrawlPresetResponse(**item) for item in response.data]

@router.get("/{preset_identifier}", response_model=CrawlPresetResponse)
async def get_crawl_preset(preset_identifier: Union[UUID, str] = Path(...)):
    query_builder = supabase_client.table("crawl_presets").select("*")
    try:
        # Attempt to convert to UUID first
        uuid_val = UUID(str(preset_identifier))
        query_builder = query_builder.eq("preset_id", uuid_val)
    except ValueError:
        # If not a UUID, assume it's a name
        query_builder = query_builder.eq("preset_name", str(preset_identifier))

    response = await query_builder.limit(1).execute() # Ensure only one record is fetched

    if response.error:
        logger.error(f"Error getting preset '{preset_identifier}': {response.error}")
        error_detail = f"Database error retrieving preset '{preset_identifier}'."
        if hasattr(response.error, 'message') and response.error.message: error_detail = str(response.error.message)
        raise HTTPException(status_code=500, detail=error_detail)
    if not response.data:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_identifier}' not found")
    return CrawlPresetResponse(**response.data[0])

@router.put("/{preset_identifier}", response_model=CrawlPresetResponse)
async def update_crawl_preset(preset_data: CrawlPresetUpdate = Body(...), preset_identifier: Union[UUID, str] = Path(...)):
    update_dict = preset_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    # RLS policies should handle ownership checks (auth.uid() = created_by)
    # The application does not need to re-verify created_by here if RLS is correctly set up.
    # update_dict["updated_at"] = datetime.now(timezone.utc).isoformat() # DB will set this with DEFAULT NOW() or trigger

    query_builder = supabase_client.table("crawl_presets").update(update_dict)
    try:
        uuid_val = UUID(str(preset_identifier))
        query_builder = query_builder.eq("preset_id", uuid_val)
    except ValueError:
        query_builder = query_builder.eq("preset_name", str(preset_identifier))

    response = await query_builder.execute()

    if response.error:
        logger.error(f"Error updating preset '{preset_identifier}': {response.error}")
        error_detail = f"Database error updating preset '{preset_identifier}'."
        if hasattr(response.error, 'message') and response.error.message: error_detail = str(response.error.message)
        raise HTTPException(status_code=400, detail=error_detail)
    if not response.data: # Supabase update returns the updated items
        raise HTTPException(status_code=404, detail=f"Preset '{preset_identifier}' not found or update failed (possibly RLS restriction or no actual change).")
    return CrawlPresetResponse(**response.data[0])

@router.delete("/{preset_identifier}", status_code=204)
async def delete_crawl_preset(preset_identifier: Union[UUID, str] = Path(...)):
    query_builder = supabase_client.table("crawl_presets").delete()
    try:
        uuid_val = UUID(str(preset_identifier))
        query_builder = query_builder.eq("preset_id", uuid_val)
    except ValueError:
        query_builder = query_builder.eq("preset_name", str(preset_identifier))

    # RLS policies should handle ownership checks.
    response = await query_builder.execute()

    if response.error:
        logger.error(f"Error deleting preset '{preset_identifier}': {response.error}")
        error_detail = f"Database error deleting preset '{preset_identifier}'."
        if hasattr(response.error, 'message') and response.error.message: error_detail = str(response.error.message)
        raise HTTPException(status_code=500, detail=error_detail)

    # Supabase delete (with supabase-py v1+) might return empty data on success if returning='minimal' (default)
    # or the deleted records if returning='representation'.
    # For a 204, we typically don't care about the response body, only that there was no error.
    # However, if no records were matched by the filter, it's effectively a 404.
    # The mock client simulates returning data if a match was hypothetically found.
    # A real client might behave differently based on `returning` option.
    # For now, let's assume if data is empty and no error, it means no record matched the ID for deletion.
    if not response.data and not response.error : # Check if data is empty AND no error
         raise HTTPException(status_code=404, detail=f"Preset '{preset_identifier}' not found.")

    return None # No content for 204 response
