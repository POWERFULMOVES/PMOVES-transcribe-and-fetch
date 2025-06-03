# Docker Compose Instructions

This document provides instructions for running the various Docker Compose configurations in this project.

## Main Application Stack

Runs the core backend, LiteLLM proxy, MinIO, Crawl4AI, Pipecat core, and agent instances.

```bash
docker-compose -f docker-compose.yml up -d --build
```

To stop:
```bash
docker-compose -f docker-compose.yml down
```

## Core Services Stack

Runs LiteLLM proxy, Crawl4AI, Pipecat core, and the Supabase agent. This is a subset of the main application stack, potentially for focused development or testing of these core components.

```bash
docker-compose -f docker-compose-core.yml up -d --build
```

To stop:
```bash
docker-compose -f docker-compose-core.yml down
```

## Pipecat Standalone (with LiteLLM)

Runs the Pipecat agent and a LiteLLM proxy. Useful for developing or testing the Pipecat agent in isolation.

```bash
docker-compose -f docker-compose.pipecat.yml up -d --build
```

To stop:
```bash
docker-compose -f docker-compose.pipecat.yml down
```

## Crawl4AI Standalone

Runs only the Crawl4AI service. Useful for testing the Crawl4AI service independently.

```bash
docker-compose -f docker-compose-crawl4ai.yml up -d --build
```

To stop:
```bash
docker-compose -f docker-compose-crawl4ai.yml down
```

## LiteLLM Proxy Standalone

Runs only the LiteLLM proxy service. Useful for testing or managing the LiteLLM proxy independently.

```bash
docker-compose -f docker-compose.litellm-proxy.yml up -d --build
```

To stop:
```bash
docker-compose -f docker-compose.litellm-proxy.yml down
```

## Supabase Agent Standalone (with LiteLLM)

Runs the Supabase agent and its own LiteLLM proxy instance. This is for focused development or testing of the Supabase agent.

```bash
docker-compose -f supabase-agent/docker-compose.yml up -d --build
```

To stop:
```bash
docker-compose -f supabase-agent/docker-compose.yml down
```

## General Notes

-   `up -d`: Starts the services in detached mode (in the background).
-   `--build`: Forces Docker Compose to rebuild the images before starting the containers. This is useful if you've made changes to Dockerfiles or the application code.
-   `down`: Stops and removes the containers, networks, and volumes created by `up`.
-   You can view logs for a specific service using `docker-compose -f <file_name.yml> logs <service_name>`. For example, `docker-compose -f docker-compose.yml logs backend`.
-   To follow logs in real-time, add the `-f` flag: `docker-compose -f <file_name.yml> logs -f <service_name>`.
-   Ensure you have Docker and Docker Compose installed and running on your system.
-   Environment variables required by the services (e.g., API keys) should be present in the respective `.env` files referenced in the compose files, or available in your shell environment if not using `.env` files directly. 