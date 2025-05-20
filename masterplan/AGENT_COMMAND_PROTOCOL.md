# PMOVES Agent Command Protocol

## Overview

This document defines the standardized protocol for communication between agents within the PMOVES platform, primarily using Pipecat as the communication layer. The core of this protocol is the `AgentCommand` structure, designed for clarity, traceability, and extensibility.

## AgentCommand Structure

All commands sent between PMOVES agents (Orchestrator to Helper, Helper to Helper, etc.) should adhere to the following JSON structure, represented in Python by the `AgentCommand` class:

```json
{
  "command_type": "string",
  "task_id": "string | null",
  "args": {
    "parameter1": "value1",
    "parameter2": "value2",
    // ... other parameters specific to the command_type
  }
}
```

### Fields:

*   `command_type` (string, required): A string identifier specifying the action the receiving agent should perform (e.g., `generate_migration`, `apply_policy`, `create_function`).
*   `task_id` (string | null, optional): A unique identifier for the task or request that this command is part of. This is crucial for distributed tracing, logging correlation, and tracking the lifecycle of complex workflows orchestrated across multiple agents. Agents should include the `task_id` from the incoming command in any responses or subsequent commands related to the same task.
*   `args` (object/JSON, optional): A dictionary containing the specific parameters required for the `command_type`. The structure and required parameters within `args` are dependent on the specific command being sent.

## Communication via Pipecat

Pipecat serves as the multimodal, real-time communication bus for PMOVES agents. `AgentCommand` objects are primarily transmitted within Pipecat `TextFrame`s. A receiving agent, acting as a `FrameProcessor` in a Pipecat pipeline, will inspect incoming frames, identify `TextFrame`s, and attempt to parse their content as an `AgentCommand`.

### Frame Flow Example (Conceptual):

1.  An Orchestrator agent decides to request a new database migration.
2.  The Orchestrator constructs an `AgentCommand` with `command_type: "generate_migration"`, a unique `task_id`, and the relevant parameters (e.g., `description`, `sql_content`) in the `args` field.
3.  The Orchestrator sends this `AgentCommand` by pushing a `TextFrame` containing the JSON representation of the command into the Pipecat pipeline connected to the Migration Agent.
4.  The Migration Agent's `process_frame` method receives the `TextFrame`.
5.  It parses the JSON content into an `AgentCommand` object.
6.  Based on the `command_type`, it calls its internal `generate_migration_file` method.
7.  Upon completion (success or failure), the Migration Agent constructs a response `AgentCommand` (e.g., `command_success`, `command_error`). This response command includes the original `task_id` and relevant results or error information in its `args`.
8.  The Migration Agent sends the response by pushing a new `TextFrame` containing the response `AgentCommand` JSON back into the pipeline (which might route it back to the Orchestrator or another designated recipient).

This flow can be visualized by understanding Pipecat's frame processing pipeline, as illustrated in documentation like `docs/pipecat/docs/images/pipeline-concept.png` (referencing existing visual aids for clarity).

### Multiple Communication Methods (Transports)

Pipecat supports various `Transport` mechanisms, enabling agents to be reachable and powerful through different communication channels:

*   **WebSocket Transport:** Useful for real-time, bidirectional communication, similar to chat interfaces or streaming data. The `docs/pipecat/examples/p2p-webrtc` and `docs/pipecat/examples/chatbot-audio-recording` examples demonstrate WebSocket usage for real-time audio and text. Helper agents could expose a WebSocket endpoint to receive `AgentCommand`s.
*   **Custom Transports:** Pipecat's flexible design allows for implementing custom transports tailored to specific needs, such as inter-process communication, message queues (like RabbitMQ or Kafka), or gRPC.
*   **HTTP (via custom FrameProcessors):** While not a core Pipecat Transport, agents can contain `FrameProcessor`s that make HTTP requests or expose HTTP endpoints, enabling integration with traditional REST services or A2A protocols over HTTP(S) as described in `docs/A2A/README.md`.

By leveraging Pipecat's pluggable transports, PMOVES agents can be designed to be reachable through the most appropriate method for their intended use case (e.g., a real-time chat agent using WebSocket, a batch processing agent using a message queue transport).

### Documentation References:

*   **Pipecat Core Concepts:** Refer to the Pipecat documentation (`docs/pipecat/docs/`) for detailed information on `Frame`s, `FrameProcessor`s, `Pipeline`s, and `Transport`s.
*   **Pipecat Examples:** Explore the examples in `docs/pipecat/examples/` to see different transport and pipeline configurations in action.
*   **Pipecat Tests:** The tests in `docs/pipecat/tests/` can provide further insight into how different Pipecat components are used.
*   **Agent2Agent (A2A) Protocol:** See `docs/A2A/README.md` for the principles behind agent discovery, capability advertising, and standardized interaction that inform the design of this command protocol and agent communication strategy.

## Helper Agent Integration

The Migration Agent, RLS Agent, and Function Creation Agent have been updated to receive and process `AgentCommand`s via their `process_frame` methods. They parse the incoming JSON, execute the requested action, and send a response `AgentCommand` back into the pipeline, including the original `task_id` for correlation.

Future steps will involve implementing specific transports for these agents and integrating them with the Agent Registry for dynamic discovery and connection management by the Orchestrator. 