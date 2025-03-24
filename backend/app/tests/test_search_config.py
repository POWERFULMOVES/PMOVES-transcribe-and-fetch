import pytest
import json
from fastapi.testclient import TestClient
from ..main import app
from ..psearchworking import SearchParameters
from ..config.search_config import DEFAULT_SEARCH_PARAMS, SEARCH_PRESETS

client = TestClient(app)

def test_get_search_config():
    """Test retrieving the current search configuration."""
    response = client.get("/api/search-config")
    assert response.status_code == 200
    data = response.json()
    
    assert "fine_grained" in data
    assert "contextual" in data
    assert "overview" in data
    
    # Check each tier has the expected parameters
    for tier in ["fine_grained", "contextual", "overview"]:
        assert "similarity_threshold" in data[tier]
        assert "content_weight" in data[tier]
        assert "result_percentage" in data[tier]
        assert "max_results" in data[tier]

def test_update_search_config():
    """Test updating the search configuration."""
    # First get the current config
    response = client.get("/api/search-config")
    original_config = response.json()
    
    # Update just the fine_grained tier
    update_data = {
        "fine_grained": {
            "similarity_threshold": 0.82,
            "max_results": 18
        }
    }
    
    response = client.post("/api/search-config", json=update_data)
    assert response.status_code == 200
    updated_config = response.json()
    
    # Check that only the specified values were updated
    assert updated_config["fine_grained"]["similarity_threshold"] == 0.82
    assert updated_config["fine_grained"]["max_results"] == 18
    assert updated_config["fine_grained"]["content_weight"] == original_config["fine_grained"]["content_weight"]
    
    # Check that other tiers remained unchanged
    assert updated_config["contextual"] == original_config["contextual"]
    assert updated_config["overview"] == original_config["overview"]
    
    # Reset to default
    client.post("/api/search-config/preset", json={"preset_name": "default"})

def test_get_presets():
    """Test retrieving the list of available presets."""
    response = client.get("/api/search-config/presets")
    assert response.status_code == 200
    data = response.json()
    
    assert "presets" in data
    assert "default" in data["presets"]
    assert "technical" in data["presets"]
    assert "conceptual" in data["presets"]
    assert "balanced" in data["presets"]

def test_get_preset_config():
    """Test retrieving a specific preset configuration."""
    # Test valid preset
    response = client.get("/api/search-config/preset/technical")
    assert response.status_code == 200
    data = response.json()
    
    # Verify data matches the preset in config
    preset = SEARCH_PRESETS["technical"]
    assert data["fine_grained"]["similarity_threshold"] == preset["fine_grained"]["similarity_threshold"]
    assert data["fine_grained"]["max_results"] == preset["fine_grained"]["max_results"]
    
    # Test invalid preset
    response = client.get("/api/search-config/preset/nonexistent")
    assert response.status_code == 404

def test_load_preset():
    """Test loading a preset configuration."""
    # Test valid preset
    response = client.post("/api/search-config/preset", json={"preset_name": "conceptual"})
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert "conceptual" in data["message"]
    
    # Verify config matches the preset
    preset = SEARCH_PRESETS["conceptual"]
    config = data["config"]
    assert config["fine_grained"]["similarity_threshold"] == preset["fine_grained"]["similarity_threshold"]
    assert config["contextual"]["content_weight"] == preset["contextual"]["content_weight"]
    
    # Test invalid preset
    response = client.post("/api/search-config/preset", json={"preset_name": "nonexistent"})
    assert response.status_code == 404

def test_vector_search_stream_with_params():
    """Test the search stream endpoint with custom parameters."""
    # This is an integration test that ensures the endpoint accepts the new parameters
    params = {
        "query": "test query",
        "fine_grained_similarity_threshold": 0.8,
        "fine_grained_content_weight": 0.9,
        "fine_grained_result_percentage": 0.5,
        "fine_grained_max_results": 10,
        "contextual_similarity_threshold": 0.7,
        "contextual_content_weight": 0.6,
        "contextual_result_percentage": 0.3,
        "contextual_max_results": 8,
        "overview_similarity_threshold": 0.6,
        "overview_content_weight": 0.4,
        "overview_result_percentage": 0.2,
        "overview_max_results": 5
    }
    
    # We just test that the endpoint accepts these parameters without error
    # (actual search functionality would be tested separately)
    with client.stream("GET", "/vector-search-stream", params=params) as response:
        assert response.status_code == 200
        # Read a few events to ensure the stream started
        for i, line in enumerate(response.iter_lines()):
            if i > 5:  # Just check the first few lines
                break
            if line.startswith(b"data: "):
                data = json.loads(line[6:])
                if data.get("type") == "error":
                    pytest.fail(f"Error in search stream: {data.get('message')}")

def test_vector_search_stream_with_preset():
    """Test the search stream endpoint with a preset parameter."""
    params = {
        "query": "test query",
        "preset": "technical"
    }
    
    with client.stream("GET", "/vector-search-stream", params=params) as response:
        assert response.status_code == 200
        for i, line in enumerate(response.iter_lines()):
            if i > 5:
                break
            if line.startswith(b"data: "):
                data = json.loads(line[6:])
                if data.get("type") == "error":
                    pytest.fail(f"Error in search stream: {data.get('message')}")
                # Look for log message indicating preset was loaded
                if data.get("type") == "log" and "preset" in data.get("message", ""):
                    break
        else:
            pytest.fail("No preset loading message found in response") 