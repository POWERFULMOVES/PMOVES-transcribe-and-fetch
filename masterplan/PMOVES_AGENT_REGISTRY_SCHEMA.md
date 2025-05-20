# PMOVES Agent Registry: Schema and Service Plan

## Overview
The PMOVES Agent Registry is a centralized service for dynamic discovery, registration, and management of all agents in the PMOVES platform. Inspired by the LiteLLM model registry, it standardizes agent metadata, supports runtime updates, and exposes APIs for orchestrators, UIs, and other services to query and interact with available agents.

---

## Agent Metadata Schema
Each agent registers with the following fields:

| Field            | Type           | Description                                                      |
|------------------|----------------|------------------------------------------------------------------|
| agent_id         | string         | Unique identifier for the agent                                  |
| name             | string         | Human-readable name                                              |
| description      | string         | Short description of the agent's purpose                         |
| capabilities     | list[string]   | List of supported actions/capabilities (e.g., fetch, summarize)  |
| input_schema     | object/JSON    | JSON schema or description of expected input                     |
| output_schema    | object/JSON    | JSON schema or description of output                             |
| status           | enum           | Agent status: active, inactive, error, etc.                      |
| endpoint         | string         | URL or IPC address for agent communication (if microservice)     |
| dependencies     | list[string]   | Required tools/services                                          |
| version          | string         | Agent version                                                    |
| tags             | list[string]   | Keywords for search/filtering                                    |
| last_heartbeat   | timestamp      | Last health check-in                                             |
| config           | object/JSON    | Optional agent-specific configuration                            |

---

## Registry Service Responsibilities
- **Registration:** Agents register themselves on startup or via config.
- **Discovery:** Expose API to list/query agents by capability, status, etc.
- **Metadata Management:** Store and update agent metadata, including health/status.
- **Dynamic Updates:** Support adding/removing agents at runtime.
- **Error Handling:** Mark agents as inactive/error if health checks fail.

---

## API Endpoint Design

The Agent Registry exposes the following REST API endpoints:

- `GET /agents`
- `GET /agents/{agent_id}`
- `POST /agents/register`
- `POST /agents/heartbeat`
- `DELETE /agents/{agent_id}`

These endpoints allow agents to manage their registration and status, and enable the Orchestrator and UI to discover and monitor available agents.

---

### `GET /agents`

*   **Method:** `GET`
*   **Purpose for Orchestrator/UI:** To discover all currently registered agents and their capabilities. The Orchestrator can use this to find suitable agents for tasks, and the UI can display a list of available agents.
*   **Request:**
    *   **Parameters:** Supports optional query parameters for filtering and searching.
        *   `capability` (string, optional): Filter agents by a specific capability (e.g., `fetch`, `summarize`).
        *   `status` (string, optional): Filter agents by their current status (e.g., `active`).
        *   `name` (string, optional): Search for agents by name.
        *   `tag` (string, optional): Filter agents by a specific tag.
    *   **Body:** None.
*   **Response:**
    *   **Status Code:** `200 OK`
    *   **Body:** A JSON array of agent objects. Each object follows the Agent Metadata Schema defined above.
    *   **Example (Orchestrator):**
        ```python
        # Conceptual Python example for Orchestrator
        import requests

        registry_url = "http://registry-service/api"
        response = requests.get(f"{registry_url}/agents?capability=summarize&status=active")

        if response.status_code == 200:
            active_summarizer_agents = response.json()
            # Orchestrator logic to select an agent
            if active_summarizer_agents:
                selected_agent = active_summarizer_agents[0]
                print(f"Found active summarizer agent: {selected_agent['name']} at {selected_agent['endpoint']}")
            else:
                print("No active summarizer agents found.")
        else:
            print(f"Error fetching agents: {response.status_code}")
        ```
    *   **Example (UI):**
        ```javascript
        // Conceptual JavaScript example for UI
        async function fetchAndDisplayAgents() {
          const registryUrl = "http://registry-service/api";
          try {
            const response = await fetch(`${registryUrl}/agents`);
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            const agents = await response.json();
            const agentListDiv = document.getElementById('agent-list');
            agentListDiv.innerHTML = agents.map(agent => `
              <div>
                <h3>${agent.name} (${agent.status})</h3>
                <p>${agent.description}</p>
                <p>Capabilities: ${agent.capabilities.join(', ')}</p>
              </div>
            `).join('');
          } catch (error) {
            console.error("Error fetching agents:", error);
            document.getElementById('agent-list').innerHTML = `<p>Error loading agents: ${error.message}</p>`;
          }
        }
        fetchAndDisplayAgents();
        ```

---

### `GET /agents/{agent_id}`

*   **Method:** `GET`
*   **Purpose for Orchestrator/UI:** To retrieve detailed information about a specific agent, typically after discovering its ID via the `GET /agents` endpoint or if the ID is known.
*   **Request:**
    *   **Parameters:**
        *   `agent_id` (string, required): The unique identifier of the agent.
    *   **Body:** None.
*   **Response:**
    *   **Status Code:** `200 OK`
    *   **Body:** A JSON object following the Agent Metadata Schema for the requested agent.
    *   **Status Code:** `404 Not Found`
    *   **Body:** JSON object with an error message, e.g., `{"detail": "Agent not found"}`.
    *   **Example (Orchestrator/UI):**
        ```python
        # Conceptual Python example
        import requests

        registry_url = "http://registry-service/api"
        agent_id_to_fetch = "summarizer-001"
        response = requests.get(f"{registry_url}/agents/{agent_id_to_fetch}")

        if response.status_code == 200:
            agent_details = response.json()
            print(f"Details for {agent_id_to_fetch}: {agent_details}")
        elif response.status_code == 404:
            print(f"Agent {agent_id_to_fetch} not found.")
        else:
            print(f"Error fetching agent details: {response.status_code}")
        ```

---

### `POST /agents/register`

*   **Method:** `POST`
*   **Purpose (primarily for Agents):** Agents use this endpoint to register themselves with the registry or update their existing registration information (e.g., capabilities, endpoint, status). The Orchestrator might also use this to register agents it spawns.
*   **Request:**
    *   **Parameters:** None.
    *   **Body:** A JSON object containing the agent's metadata, following the Agent Metadata Schema. The `agent_id` is required in the body for registration/update.
    *   **Example Request Body:** See the example provided in the main section of this document.
*   **Response:**
    *   **Status Code:** `201 Created` (if new agent registered)
    *   **Status Code:** `200 OK` (if existing agent updated)
    *   **Body:** A JSON object representing the registered/updated agent's metadata.
    *   **Status Code:** `400 Bad Request`
    *   **Body:** JSON object with error details, e.g., `{"detail": "Invalid agent data"}`.
    *   **Example (Agent/Orchestrator):**
        ```python
        # Conceptual Python example for an Agent registering
        import requests
        import json
        import uuid

        registry_url = "http://registry-service/api"
        agent_metadata = {
          "agent_id": str(uuid.uuid4()), # Generate unique ID on first registration
          "name": "MyNewAgent",
          "description": "Performs a specific task.",
          "capabilities": ["process_data"],
          "input_schema": {}, # Define schema
          "output_schema": {}, # Define schema
          "status": "active",
          "endpoint": "http://localhost:5002/api",
          "dependencies": [],
          "version": "1.0.0",
          "tags": ["utility"],
          "last_heartbeat": "2024-06-01T12:05:00Z", # Include current timestamp
          "config": {}
        }

        response = requests.post(f"{registry_url}/agents/register", json=agent_metadata)

        if response.status_code in [200, 201]:
            registered_agent = response.json()
            print(f"Agent registered/updated successfully: {registered_agent['agent_id']}")
        else:
            print(f"Error registering agent: {response.status_code}, {response.text}")
        ```

---

### `POST /agents/heartbeat`

*   **Method:** `POST`
*   **Purpose (primarily for Agents):** Agents send periodic heartbeats to this endpoint to indicate they are still active and healthy. The registry uses this to track agent liveness.
*   **Request:**
    *   **Parameters:** None.
    *   **Body:** A JSON object containing the agent's ID and optionally its current status and a timestamp.
        *   `agent_id` (string, required): The unique identifier of the agent sending the heartbeat.
        *   `status` (string, optional): The agent's current status (e.g., `active`, `busy`, `error`). Defaults to `active` if not provided.
        *   `last_heartbeat` (timestamp, optional): The timestamp of the heartbeat. Defaults to the server's current time if not provided.
*   **Response:**
    *   **Status Code:** `200 OK`
    *   **Body:** A confirmation JSON object, e.g., `{"message": "Heartbeat received"}`.
    *   **Status Code:** `404 Not Found`
    *   **Body:** JSON object with an error message, e.g., `{"detail": "Agent not found"}` (if the agent ID is not registered).
    *   **Status Code:** `400 Bad Request`
    *   **Body:** JSON object with error details, e.g., `{"detail": "agent_id is required"}`.
    *   **Example (Agent):**
        ```python
        # Conceptual Python example for an Agent sending a heartbeat
        import requests
        import json
        from datetime import datetime

        registry_url = "http://registry-service/api"
        agent_id = "summarizer-001" # The agent's registered ID

        heartbeat_payload = {
          "agent_id": agent_id,
          "status": "active", # Optional: Send current status
          "last_heartbeat": datetime.now().isoformat() # Optional: Send timestamp
        }

        response = requests.post(f"{registry_url}/agents/heartbeat", json=heartbeat_payload)

        if response.status_code == 200:
            print(f"Heartbeat sent for {agent_id}")
        elif response.status_code == 404:
            print(f"Agent {agent_id} not found in registry.")
        else:
            print(f"Error sending heartbeat: {response.status_code}, {response.text}")
        ```

---

### `DELETE /agents/{agent_id}`

*   **Method:** `DELETE`
*   **Purpose (primarily for Orchestrator/Agent cleanup):** Used to deregister an agent when it is shutting down gracefully or when the Orchestrator determines it is no longer needed or is unhealthy.
*   **Request:**
    *   **Parameters:**
        *   `agent_id` (string, required): The unique identifier of the agent to deregister.
    *   **Body:** None.
*   **Response:**
    *   **Status Code:** `200 OK`
    *   **Body:** A confirmation JSON object, e.g., `{"message": "Agent deregistered"}`.
    *   **Status Code:** `404 Not Found`
    *   **Body:** JSON object with an error message, e.g., `{"detail": "Agent not found"}` (if the agent ID is not registered).
    *   **Example (Orchestrator/Agent):**
        ```python
        # Conceptual Python example for deregistering an agent
        import requests

        registry_url = "http://registry-service/api"
        agent_id_to_delete = "summarizer-001"

        response = requests.delete(f"{registry_url}/agents/{agent_id_to_delete}")

        if response.status_code == 200:
            print(f"Agent {agent_id_to_delete} deregistered successfully.")
        elif response.status_code == 404:
            print(f"Agent {agent_id_to_delete} not found in registry.")
        else:
            print(f"Error deregistering agent: {response.status_code}, {response.text}")
        ```

---

## Authentication and Authorization (Future Consideration)

*   For a production system, implement authentication and authorization to secure the registry endpoints.
*   Agents might require a token to register or send heartbeats.
*   Orchestrators and UIs might require different permissions to read or delete agent registrations.

## Error Handling

*   The API should return appropriate HTTP status codes (e.g., 200, 201, 400, 404, 500).
*   Error responses should include a JSON body with an informative `detail` or `message` field.

---

## Next Steps
1. Implement a minimal registry service (REST API, in-memory or file-based)
2. Prototype agent self-registration and heartbeat
3. Document registry API and usage for orchestrator and UI
4. Plan for persistent storage and scaling as needed 