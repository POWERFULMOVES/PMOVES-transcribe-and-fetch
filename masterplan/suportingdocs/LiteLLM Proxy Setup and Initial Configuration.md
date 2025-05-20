# LiteLLM Proxy Setup and Initial Configuration

## Progress & Next Steps

### ✅ Progress So Far
- The `litellm_proxy_config/config.yaml` has been updated with a comprehensive set of model aliases for all major model types and endpoints (chat, vision, embedding, audio, image, etc.) for all wishlist providers.
- This documentation has been created to guide setup, usage, and verification.

### ⏭️ Next Steps
1. **Set Environment Variables**
   - Ensure all required environment variables are present in your `.env` file (see Section 2 below).
2. **Update Docker Compose**
   - Make sure `docker-compose.litellm-proxy.yml` mounts the updated config and passes all necessary environment variables.
3. **Start/Restart the Proxy**
   - Use Docker Compose to start or restart the LiteLLM proxy with the new configuration.
4. **Verify the Proxy**
   - Use the `/v1/models` and `/model/info` endpoints to confirm all aliases are available (see updated instructions below).
5. **Test Example Requests**
   - Try the example requests in Section 5 to ensure each alias works as expected.
6. **Integration & Automation**
   - Integrate the proxy with your backend/frontend as needed.
   - (Optional) Add or update integration tests to verify all endpoints and aliases.

---

## Overview
This guide explains how to set up the LiteLLM proxy, configure it with a comprehensive set of model aliases for all major model types and endpoints, and use these aliases for various LLM tasks (chat, vision, embedding, audio, image, etc.).

---

## 1. Configuration File (`litellm_proxy_config/config.yaml`)

The proxy is configured via `litellm_proxy_config/config.yaml`. This file now includes aliases for all major model types and endpoints for each supported provider (OpenAI, Anthropic, Deepseek, Perplexity, Nvidia NIM, Hugging Face, LM Studio, etc.).

### Example Alias Mapping
| Alias                        | Model Route / Type         | Provider      | Example Use Case           |
|------------------------------|----------------------------|---------------|---------------------------|
| openai-gpt-4o-chat           | openai/gpt-4o (chat)       | OpenAI        | Chat/Completion           |
| openai-gpt-4o-vision         | openai/gpt-4o (vision)     | OpenAI        | Vision (image+text input) |
| openai-text-embedding-ada-002| openai/text-embedding-ada-002 | OpenAI    | Embedding                |
| openai-whisper-1             | openai/whisper-1 (audio)   | OpenAI        | Audio transcription       |
| openai-tts-1                 | openai/tts-1 (audio)       | OpenAI        | Text-to-speech            |
| openai-dall-e-3              | openai/dall-e-3 (image)    | OpenAI        | Image generation          |
| anthropic-claude-3.5-chat    | anthropic/claude-3.5-sonnet-20240620 | Anthropic | Chat/Completion |
| deepseek-chat                | deepseek/deepseek-chat     | Deepseek      | Chat/Completion           |
| perplexity-sonar-pro         | perplexity/sonar-pro       | Perplexity AI | Chat/Completion           |
| nvidia-nim-llama3-8b-chat    | nvidia_nim/meta/llama3-8b-instruct | Nvidia NIM | Chat/Completion |
| hf-mistral-7b-instruct-chat  | huggingface/together/mistralai/Mistral-7B-Instruct-v0.1 | Hugging Face | Chat/Completion |
| hf-llama3-vision             | huggingface/sambanova/meta-llama/Llama-3.2-11B-Vision-Instruct | Hugging Face | Vision |
| hf-mistral-embed             | huggingface/together/mistralai/Mistral-Embed | Hugging Face | Embedding |
| hf-whisper-audio             | huggingface/openai/whisper-large | Hugging Face | Audio transcription |
| hf-stable-diffusion-image    | huggingface/stabilityai/stable-diffusion-xl-base-1.0 | Hugging Face | Image generation |
| lmstudio-llama3-8b-chat      | lm_studio/llama-3-8b-instruct | LM Studio | Chat/Completion |

---

## 2. Environment Variables

Ensure all required environment variables are set in your `.env` file:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `DEEPSEEK_API_KEY`
- `PERPLEXITYAI_API_KEY`
- `NVIDIA_NIM_API_KEY`
- `HF_TOKEN`
- `LM_STUDIO_API_BASE`

Add any others required for your specific providers/models.

---

## 3. Docker Compose Setup

- Make sure your `docker-compose.litellm-proxy.yml` mounts the updated config and passes all necessary environment variables.

### Docker Compose Commands for Proxy Only
To build, start, or restart only the LiteLLM proxy service (recommended for most changes):

- **Build and start only the proxy:**
  ```powershell
  docker compose up -d --build litellm-proxy
  ```
- **Restart only the proxy (no rebuild):**
  ```powershell
  docker compose up -d litellm-proxy
  ```
- **Build and start all services (rarely needed):**
  ```powershell
  docker compose up -d --build
  ```

> **Tip:** Always specify the service name (`litellm-proxy`) at the end of the command to target just that container. This avoids unnecessary rebuilds or restarts of other services in your stack.

---

## Docker Logs & Debugging

Monitoring and debugging your LiteLLM proxy container is essential for troubleshooting and ensuring smooth operation. Here are the most up-to-date ways to view and debug logs:

**Note:** For this project, the proxy container name is set to `litellm-proxy` in `docker-compose.litellm-proxy.yml`. Use this name in all commands below unless you have changed it.

### Windows PowerShell Tips
If you are running Docker Desktop and using PowerShell on Windows, use these commands for troubleshooting:

**1. Check config.yaml exists and is not empty:**
```powershell
Get-Content .\litellm_proxy_config\config.yaml | Select-Object -First 20
```

**2. Check file is mounted inside the container:**
```powershell
docker exec -it litellm-proxy powershell
# Then inside the container (if PowerShell is available):
cat C:\app\config.yaml
# Or, if using Linux shell inside the container:
cat /app/config.yaml
```

**3. Check CONFIG_PATH environment variable inside the container:**
```powershell
docker exec -it litellm-proxy powershell -Command "echo $env:CONFIG_PATH"
# Or, if using Linux shell:
docker exec -it litellm-proxy printenv CONFIG_PATH
```

**4. Get Docker logs:**
```powershell
docker logs litellm-proxy --tail 50
```

**5. Restart the proxy:**
```powershell
docker compose down
docker compose up -d
```

**6. Check the last 50 lines of your config file:**
```powershell
Get-Content .\litellm_proxy_config\config.yaml | Select-Object -Last 50
```

**7. File Sharing:**
Make sure Docker Desktop has access to your project directory (Docker Desktop > Settings > Resources > File Sharing).

### 1. View Logs for the Proxy Container
```bash
docker compose logs litellm-proxy
# or
docker logs litellm-proxy
```

### 2. Follow Logs in Real Time
```bash
docker compose logs --follow litellm-proxy
# or
docker logs -f litellm-proxy
```

### 3. Filter Logs
- Show only the last N lines:
  ```bash
  docker compose logs --tail 20 litellm-proxy
  # or
  docker logs --tail 20 litellm-proxy
  ```
- Show logs since a specific time:
  ```bash
  docker compose logs --since 1h litellm-proxy
  # or
  docker logs --since 1h litellm-proxy
  ```
- Combine with follow:
  ```bash
  docker compose logs --follow --tail 10 litellm-proxy
  ```

### 4. Advanced Debugging with Docker Debug (Docker Desktop 4.33+)
If your container is very minimal or you need a shell for deep inspection:
```bash
docker debug litellm-proxy
```
This gives you a debug shell even if the container doesn't have one. See [Docker Debug docs](https://docs.docker.com/reference/cli/docker/debug/) for more.

### 5. Troubleshooting Tips
- If logs are empty:
  - Ensure your app writes logs to stdout/stderr (not just to files inside the container).
  - Check that the container is running and not restarting or exited.
  - Use `docker inspect litellm-proxy` to check log driver and log file path.
- For persistent issues, check Docker daemon logs:
  ```bash
  sudo journalctl -u docker
  ```
- For GUI log viewing, try Docker Desktop's Logs tab or a tool like [Dozzle](https://github.com/amir20/dozzle).

**References:**
- [Docker Container Logs: A Comprehensive Guide](https://betterstack.com/community/guides/logging/docker-logs/)
- [Docker Compose Logs: Monitoring & Debugging](https://spacelift.io/blog/docker-compose-logs)
- [Docker Debug CLI Reference](https://docs.docker.com/reference/cli/docker/debug/)

---

## 4. Verifying the Proxy

- After starting, check the `/v1/models` endpoint to see all available aliases:
  ```bash
  curl http://localhost:4000/v1/models
  ```
- For detailed model info, use:
  ```bash
  curl http://localhost:4000/model/info
  ```
- You should see all the aliases listed in your config.

### Troubleshooting
- If you get an empty list or unexpected results:
  - Ensure the proxy is running with the correct config file.
  - Check that all required environment variables are set and available to the proxy container.
  - Some endpoints may require an API key; check your proxy logs for authentication errors.
  - Review proxy logs for any startup or runtime errors.

---

## 5. Example Requests

### Chat/Completion
```bash
curl -X POST http://localhost:4000/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "openai-gpt-4o-chat",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Vision (Image + Text)
```bash
curl -X POST http://localhost:4000/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "openai-gpt-4o-vision",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "What is in this image?"},
        {"type": "image_url", "image_url": {"url": "https://example.com/image.png"}}
      ]
    }]
  }'
```

### Embedding
```bash
curl -X POST http://localhost:4000/embeddings \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "openai-text-embedding-ada-002",
    "input": ["Hello world"]
  }'
```

### Audio Transcription
```bash
curl -X POST http://localhost:4000/audio/transcriptions \
  -H 'Content-Type: multipart/form-data' \
  -F "model=openai-whisper-1" \
  -F "file=@/path/to/audio.mp3"
```

### Text-to-Speech
```bash
curl -X POST http://localhost:4000/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "openai-tts-1",
    "input": "Hello world"
  }'
```

### Image Generation
```bash
curl -X POST http://localhost:4000/images \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "openai-dall-e-3",
    "prompt": "A beautiful sunset over mountains"
  }'
```

---

## 6. Supported Endpoints

- `/chat/completions` (chat, vision)
- `/embeddings` (embedding)
- `/audio/transcriptions`, `/audio/speech` (audio)
- `/images` (image generation)
- `/responses` (OpenAI Response API)

See the [LiteLLM Supported Endpoints](https://docs.litellm.ai/docs/supported_endpoints) for more details.

---

## 7. Troubleshooting
- Ensure all environment variables are set and available to the proxy container.
- Check logs for errors if a model/alias is not available.
- Use `/models` endpoint to verify available models.

---

## 8. References
- [LiteLLM Supported Endpoints](https://docs.litellm.ai/docs/supported_endpoints)
- [LiteLLM Providers](https://docs.litellm.ai/docs/providers)
- Your `litellm_proxy_config/config.yaml`

---

This setup ensures you can flexibly and centrally manage all your LLM models and capabilities via the LiteLLM proxy. 