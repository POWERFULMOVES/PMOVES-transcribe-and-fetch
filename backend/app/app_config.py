# NOTE: This is the ONLY config file for backend settings.
# Do not use or create alternate config files for Whisper or API keys.
# All settings should come from .env or this file.
import os
from dotenv import load_dotenv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the current directory (where config.py is)
current_dir = Path(__file__).parent
env_path = current_dir / '.env'

logger.info(f"Looking for .env file at: {env_path}")
# Force reload of environment variables
load_dotenv(env_path, override=True)

# Unified workspace root
WORKSPACE_ROOT = os.getenv('WORKSPACE_ROOT', os.path.join(os.getcwd(), 'workspace'))

# Centralized subfolder structure for all content types
SUBFOLDERS = {
    "transcriptions": {
        "audio": "audio",
        "markdown": "markdown",
        "pdf": "pdf"
    },
    "downloads": {
        "video": "video",
        "audio": "audio",
        "subtitles": "subtitles"
    },
    "fetches": {
        "markdown": "markdown",
        "pdf": "pdf"
    },
    "uploads": {
        "files": "files",
        "metadata": "metadata"
    }
}

# Path to wkhtmltopdf executable
WKHTMLTOPDF_PATH = os.getenv('WKHTMLTOPDF_PATH', 'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
if not os.path.isfile(WKHTMLTOPDF_PATH):
    logger.warning(
        f"wkhtmltopdf not found at '{WKHTMLTOPDF_PATH}'. "
        f"PDF generation will fail unless properly configured. "
        f"Please install wkhtmltopdf or set WKHTMLTOPDF_PATH in .env file."
    )

# Whisper model settings
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'large-v3')
WHISPER_DEVICE = os.getenv('WHISPER_DEVICE', 'cuda')
WHISPER_COMPUTE_TYPE = os.getenv('WHISPER_COMPUTE_TYPE', 'float16')


# API Key and Base URL Environment Variables
# Centralized loading of API keys and base URLs from environment variables
# crawl4ai will attempt to load these if a token is not explicitly passed.
# Defining them here makes it clear what the application expects.
GOOGLE_API_KEY= os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') # crawl4ai docs show GEMINI_API_KEY and GEMINI_API_TOKEN, using KEY for consistency
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
TOGETHER_AI_API_KEY = os.getenv('TOGETHER_AI_API_KEY')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
FIREWORKS_AI_API_KEY = os.getenv('FIREWORKS_AI_API_KEY') # Assuming FIREWORKS_AI_API_KEY based on provider name
PERPLEXITYAI_API_KEY= os.getenv('PERPLEXITYAI_API_KEY')
# Base URLs for local/custom OpenAI-compatible endpoints
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434') # Default for local Ollama
OPENAI_COMPATIBLE_BASE_URL = os.getenv('OPENAI_COMPATIBLE_BASE_URL') # For LM Studio, etc.

# Model configurations
# Keys are user-friendly display names.
# Each entry contains:
#   - id: The `provider_name/model_name` string crawl4ai expects.
#   - description: User-friendly description.
#   - provider_group: Helps categorize models in UI (e.g., "OpenAI", "Groq").
#   - requires_api_key: Boolean.
#   - api_key_var: Name of the environment variable for the API key (if required).
#   - base_url_var: Name of the environment variable for the base URL (if applicable).
#   - is_llm_provider: Boolean, true if it's an LLM for crawl4ai's LLMConfig.
#   - type: 'llm' or 'transcription'
AVAILABLE_MODELS = {
    # Faster Whisper (Local) - Special case
    'Faster Whisper (Local Transcription)': {
        'id': 'faster-whisper', # Internal identifier, not for crawl4ai LLMConfig
        'description': 'Local Faster Whisper model for audio transcription',
        'provider_group': 'Local Models',
        'type': 'transcription',
        'requires_gpu': True,
        'is_llm_provider': False # Not used with LLMConfig in crawl4ai
    },

    # OpenAI
    "OpenAI: GPT-4o": { # General availability, often points to latest
        "id": "openai/gpt-4o",
        "description": "OpenAI's most advanced multimodal model.",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: GPT-4o Mini": { # General availability
        "id": "openai/gpt-4o-mini",
        "description": "OpenAI's most capable and cost-effective small model.",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: GPT-4.1 Mini (2025-04-14)": { # Specific version from Azure/User
        "id": "openai/gpt-4.1-mini-2025-04-14", # Assuming crawl4ai uses this ID format
        "description": "OpenAI GPT-4.1 Mini (specific version).",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: GPT-4.1 Nano (2025-04-14)": { # Specific version from Azure/User
        "id": "openai/gpt-4.1-nano-2025-04-14", # Assuming crawl4ai uses this ID format
        "description": "OpenAI GPT-4.1 Nano, fastest 4.1 model (specific version).",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: o4-mini (2025-04-16)": { # Specific version from Azure/User
        "id": "openai/o4-mini-2025-04-16", # Assuming crawl4ai uses this ID format
        "description": "OpenAI o4-mini reasoning model (specific version).",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: GPT-4 Turbo (latest)": { # General Turbo, often points to latest like turbo-2024-04-09
        "id": "openai/gpt-4-turbo",
        "description": "OpenAI GPT-4 Turbo with 128k context (latest general availability).",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI: GPT-3.5 Turbo (latest)": {
        "id": "openai/gpt-3.5-turbo",
        "description": "OpenAI GPT-3.5 Turbo, fast and affordable (latest general availability).",
        "provider_group": "OpenAI",
        "requires_api_key": True, "api_key_var": "OPENAI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Groq
    "Groq: Llama 3.3 70B Versatile": { # New from Groq Docs
        "id": "groq/llama-3.3-70b-versatile",
        "description": "Meta Llama 3.3 70B (128k context) via Groq.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Llama3 70B (8k context)": { # Retained, still in Groq production
        "id": "groq/llama3-70b-8192",
        "description": "Meta Llama3 70B (8k context) via Groq, very fast.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Llama 3.1 8B Instant": { # New from Groq Docs
        "id": "groq/llama-3.1-8b-instant",
        "description": "Meta Llama 3.1 8B (128k context) via Groq.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Llama3 8B (8k context)": { # Retained, still in Groq production
        "id": "groq/llama3-8b-8192",
        "description": "Meta Llama3 8B (8k context) via Groq, very fast.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Mixtral 8x7B (32k context)": { # Retained, popular Groq model
        "id": "groq/mixtral-8x7b-32768",
        "description": "Mixtral 8x7B (32k context) via Groq, very fast.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Gemma2 9B IT": { # New from Groq Docs (replaces gemma-7b-it)
        "id": "groq/gemma2-9b-it",
        "description": "Google Gemma2 9B IT (8k context) via Groq.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: DeepSeek-R1 Distill Llama 70B (Preview)": { # User requested, from Groq Preview
        "id": "groq/deepseek-r1-distill-llama-70b",
        "description": "DeepSeek-R1 Distill Llama 70B (128k context, Preview) via Groq.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Groq: Llama Guard 3 8B": { # New from Groq Docs, likely for moderation
        "id": "groq/llama-guard-3-8b",
        "description": "Meta Llama Guard 3 8B (8k context) via Groq, for content moderation.",
        "provider_group": "Groq",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": True, # crawl4ai might treat it as a standard LLM
        "type": "llm" # Or potentially 'moderation' if app handles it differently
    },

    # Groq Transcription Models (User Requested)
    "Groq: Whisper Large v3 Turbo (Transcription)": {
        "id": "groq/whisper-large-v3-turbo",
        "description": "OpenAI Whisper Large v3 Turbo via Groq for audio transcription.",
        "provider_group": "Groq (Transcription)",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": False, # Not for LLMConfig text generation
        "type": "transcription"
    },
    "Groq: Distil-Whisper Large v3 EN (Transcription)": {
        "id": "groq/distil-whisper-large-v3-en",
        "description": "HuggingFace Distil-Whisper Large v3 EN via Groq for English audio transcription.",
        "provider_group": "Groq (Transcription)",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": False, # Not for LLMConfig text generation
        "type": "transcription"
    },

    # Groq TTS Models (User Requested)
    "Groq: PlayAI TTS (Preview)": {
        "id": "groq/playai-tts",
        "description": "PlayAI Text-to-Speech (Preview) via Groq.",
        "provider_group": "Groq (TTS)",
        "requires_api_key": True, "api_key_var": "GROQ_API_KEY",
        "is_llm_provider": False, # Not for LLMConfig text generation
        "type": "tts"
    },

    # Anthropic
    "Anthropic: Claude 3.5 Sonnet": { # Newest Sonnet
        "id": "anthropic/claude-3-5-sonnet-20240620",
        "description": "Anthropic's latest Sonnet model, balances speed and intelligence.",
        "provider_group": "Anthropic",
        "requires_api_key": True, "api_key_var": "ANTHROPIC_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Anthropic: Claude 3 Opus": {
        "id": "anthropic/claude-3-opus-20240229",
        "description": "Anthropic's most powerful model, Claude 3 Opus.",
        "provider_group": "Anthropic",
        "requires_api_key": True, "api_key_var": "ANTHROPIC_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Anthropic: Claude 3 Sonnet (Original)": {
        "id": "anthropic/claude-3-sonnet-20240229",
        "description": "Anthropic Claude 3 Sonnet (original release), balanced performance.",
        "provider_group": "Anthropic",
        "requires_api_key": True, "api_key_var": "ANTHROPIC_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Anthropic: Claude 3 Haiku": {
        "id": "anthropic/claude-3-haiku-20240307",
        "description": "Anthropic's fastest and most compact model, Claude 3 Haiku.",
        "provider_group": "Anthropic",
        "requires_api_key": True, "api_key_var": "ANTHROPIC_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Google Gemini
    "Google: Gemini 2.5 Pro Preview (05-06)": { # From Google Docs
        "id": "gemini/gemini-2.5-pro-preview-05-06", # Model code: models/gemini-2.5-pro-preview-05-06
        "description": "Google's state-of-the-art thinking model (Preview).",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Google: Gemini 2.5 Flash Preview (04-17)": { # User requested
        "id": "gemini/gemini-2.5-flash-preview-04-17", # Model code: models/gemini-2.5-flash-preview-04-17
        "description": "Google's best price-performance model (Preview).",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Google: Gemini 2.0 Flash Live (001)": { # User requested
        "id": "gemini/gemini-2.0-flash-live-001", # Model code: models/gemini-2.0-flash-live-001
        "description": "Google Gemini for low-latency bidirectional voice and video interactions.",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm" # Can output text and audio
    },
    "Google: Gemini 1.5 Pro (latest)": { # Retained from previous, still current
        "id": "gemini/gemini-1.5-pro-latest", # Model code: models/gemini-1.5-pro (latest points to this)
        "description": "Google's mid-size multimodal model for complex reasoning.",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Google: Gemini 1.5 Flash (latest)": { # Retained from previous, still current
        "id": "gemini/gemini-1.5-flash-latest", # Model code: models/gemini-1.5-flash (latest points to this)
        "description": "Google's fast and versatile multimodal model.",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Google: Gemini Embedding (Experimental)": { # User requested
        "id": "gemini/gemini-embedding-exp-03-07", # Model code from docs: gemini-embedding-exp-03-07
        "description": "Google's experimental text embedding model.",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": False, # Primarily for embeddings, not general LLM tasks via LLMConfig
        "type": "embedding"
    },
    "Google: Gemini Pro (legacy)": { # As per crawl4ai docs, kept for compatibility
        "id": "gemini/gemini-pro",
        "description": "Google Gemini Pro (legacy version, from crawl4ai docs).",
        "provider_group": "Google Gemini",
        "requires_api_key": True, "api_key_var": "GEMINI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # DeepSeek (API)
    "DeepSeek API: Chat": {
        "id": "deepseek/deepseek-chat",
        "description": "DeepSeek Chat model via API.",
        "provider_group": "DeepSeek (API)",
        "requires_api_key": True, "api_key_var": "DEEPSEEK_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "DeepSeek API: Coder": {
        "id": "deepseek/deepseek-coder",
        "description": "DeepSeek Coder model via API, specialized for code.",
        "provider_group": "DeepSeek (API)",
        "requires_api_key": True, "api_key_var": "DEEPSEEK_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Mistral AI (API)
    "Mistral API: Large (latest)": {
        "id": "mistral/mistral-large-latest",
        "description": "Mistral AI's flagship model, Large (latest) via API.",
        "provider_group": "Mistral AI (API)",
        "requires_api_key": True, "api_key_var": "MISTRAL_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Mistral API: Small (latest)": { # Mistral often refers to this as `mistral-small-latest`
        "id": "mistral/mistral-small-latest", # crawl4ai might just use `mistral/mistral-small`
        "description": "Mistral AI's Small model (latest) via API, optimized for latency.",
        "provider_group": "Mistral AI (API)",
        "requires_api_key": True, "api_key_var": "MISTRAL_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Mistral API: Codestral (latest)": {
        "id": "mistral/codestral-latest",
        "description": "Mistral AI's Codestral model for code generation (latest) via API.",
        "provider_group": "Mistral AI (API)",
        "requires_api_key": True, "api_key_var": "MISTRAL_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    # Note: open-mixtral-8x7b is often served by other providers like TogetherAI or Groq,
    # or locally via Ollama. If Mistral offers it directly via their API, it would be listed here.

    # Together AI
    "TogetherAI: Llama 3 70B Chat HF": {
        "id": "together_ai/meta-llama/Llama-3-70b-chat-hf",
        "description": "Llama 3 70B Chat (HuggingFace version) via Together AI.",
        "provider_group": "Together AI",
        "requires_api_key": True, "api_key_var": "TOGETHER_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "TogetherAI: Llama 3 8B Chat HF": {
        "id": "together_ai/meta-llama/Llama-3-8b-chat-hf",
        "description": "Llama 3 8B Chat (HuggingFace version) via Together AI.",
        "provider_group": "Together AI",
        "requires_api_key": True, "api_key_var": "TOGETHER_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "TogetherAI: Mixtral 8x7B Instruct": {
        "id": "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
        "description": "Mixtral 8x7B Instruct v0.1 via Together AI.",
        "provider_group": "Together AI",
        "requires_api_key": True, "api_key_var": "TOGETHER_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "TogetherAI: Qwen1.5 72B Chat": {
        "id": "together_ai/Qwen/Qwen1.5-72B-Chat",
        "description": "Qwen 1.5 72B Chat via Together AI.",
        "provider_group": "Together AI",
        "requires_api_key": True, "api_key_var": "TOGETHER_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Cohere
    "Cohere: Command R+": {
        "id": "cohere/command-r-plus",
        "description": "Cohere's most advanced model, Command R+.",
        "provider_group": "Cohere",
        "requires_api_key": True, "api_key_var": "COHERE_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Cohere: Command R": {
        "id": "cohere/command-r",
        "description": "Cohere Command R model.",
        "provider_group": "Cohere",
        "requires_api_key": True, "api_key_var": "COHERE_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Cohere: Command Light": { # General Command and Command Light
        "id": "cohere/command-light",
        "description": "Cohere Command Light, faster and more affordable.",
        "provider_group": "Cohere",
        "requires_api_key": True, "api_key_var": "COHERE_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Fireworks AI
    "Fireworks AI: Llama v3 70B Instruct": {
        "id": "fireworks_ai/accounts/fireworks/models/llama-v3-70b-instruct",
        "description": "Llama v3 70B Instruct via Fireworks AI.",
        "provider_group": "Fireworks AI",
        "requires_api_key": True, "api_key_var": "FIREWORKS_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Fireworks AI: Mixtral 8x7B Instruct": {
        "id": "fireworks_ai/accounts/fireworks/models/mixtral-8x7b-instruct",
        "description": "Mixtral 8x7B Instruct via Fireworks AI.",
        "provider_group": "Fireworks AI",
        "requires_api_key": True, "api_key_var": "FIREWORKS_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },
    "Fireworks AI: Firefunction V1": {
        "id": "fireworks_ai/accounts/fireworks/models/firefunction-v1",
        "description": "Firefunction V1 (Function Calling Model) via Fireworks AI.",
        "provider_group": "Fireworks AI",
        "requires_api_key": True, "api_key_var": "FIREWORKS_AI_API_KEY",
        "is_llm_provider": True, "type": "llm"
    },

    # Ollama (Local models) - Updated based on user request and ollama.com/library
    "Ollama: Llama 3.3 (local)": { # User requested
        "id": "ollama/llama3.3",
        "description": "Llama 3.3 model running locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: DeepSeek-R1 (local)": { # User requested
        "id": "ollama/deepseek-r1",
        "description": "DeepSeek's first-generation reasoning model locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: Qwen 3 (local)": { # User requested
        "id": "ollama/qwen3",
        "description": "Qwen3 model series locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: Mistral (local)": { # User requested
        "id": "ollama/mistral", # This is typically mistral-7b
        "description": "Mistral 7B model (v0.3) running locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: Gemma 3 (local)": { # User requested
        "id": "ollama/gemma3",
        "description": "Gemma 3 model series locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: Phi-4 Reasoning (local)": { # User requested (phi4)
        "id": "ollama/phi4",
        "description": "Phi-4 (14B) reasoning model locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: Phi-4 Mini Reasoning (local)": { # User requested and confirmed
        "id": "ollama/phi4-mini-reasoning",
        "description": "Phi-4 Mini (3.8B) reasoning model locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    # Retaining some common Ollama models from previous list if not covered above
    "Ollama: Llama3 (generic, local)": {
        "id": "ollama/llama3",
        "description": "Generic Llama3 model (e.g., 8B) locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "Ollama: CodeLlama (local)": {
        "id": "ollama/codellama",
        "description": "CodeLlama model running locally via Ollama.",
        "provider_group": "Ollama (Local)",
        "requires_api_key": False, "base_url_var": "OLLAMA_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },


    # OpenAI-Compatible (e.g., LM Studio)
    "OpenAI-Compatible: LM Studio (local)": {
        "id": "openai/lm-studio-model", # Placeholder, actual model depends on server
        "description": "Model served by LM Studio or other local OpenAI-compatible server.",
        "provider_group": "OpenAI-Compatible (Local)",
        "requires_api_key": False,
        "api_key_var": "OPENAI_API_KEY", # Often a dummy key like "lm-studio" is accepted
        "base_url_var": "OPENAI_COMPATIBLE_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    },
    "OpenAI-Compatible: Another Local Model": {
        "id": "openai/another-local-model", # Placeholder
        "description": "Another model via a local OpenAI-compatible server.",
        "provider_group": "OpenAI-Compatible (Local)",
        "requires_api_key": False,
        "api_key_var": "OPENAI_API_KEY",
        "base_url_var": "OPENAI_COMPATIBLE_BASE_URL",
        "is_llm_provider": True, "type": "llm"
    }
}

# Debug logging for loaded API keys
API_KEYS_TO_LOG = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
    "GROQ_API_KEY": GROQ_API_KEY,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "DEEPSEEK_API_KEY": DEEPSEEK_API_KEY,
    "MISTRAL_API_KEY": MISTRAL_API_KEY,
    "PERPLEXITYAI_API_KEY": PERPLEXITYAI_API_KEY,
    "TOGETHER_AI_API_KEY": TOGETHER_AI_API_KEY,
    "COHERE_API_KEY": COHERE_API_KEY,
    "FIREWORKS_AI_API_KEY": FIREWORKS_AI_API_KEY,
}

for key_name, key_value in API_KEYS_TO_LOG.items():
    logger.info(f"{key_name} loaded: {'Yes' if key_value else 'No'}")
    if not key_value:
        logger.warning(f"{key_name} is not set in environment variables.")
    elif key_value == f"your_{key_name.lower()}_here" or "sk-YOUR_KEY_HERE" in key_value: # Common placeholder patterns
        logger.error(f"Default placeholder value detected for {key_name} - please update your .env file.")
    else:
        logger.info(f"{key_name} starts with: {key_value[:min(len(key_value), 5)]}...")


# Debug logging for Base URLs
BASE_URLS_TO_LOG = {
    "OLLAMA_BASE_URL": OLLAMA_BASE_URL,
    "OPENAI_COMPATIBLE_BASE_URL": OPENAI_COMPATIBLE_BASE_URL,
}
for url_name, url_value in BASE_URLS_TO_LOG.items():
    logger.info(f"{url_name} loaded: {url_value if url_value else 'Not set, using default or none'}")
    if url_value and ("localhost" in url_value or "127.0.0.1" in url_value):
        logger.info(f"{url_name} appears to be a local address: {url_value}")

# --- LiteLLM Proxy and LLM Registry Configuration ---
LITELLM_PROXY_URL = os.getenv('LITELLM_PROXY_URL', 'http://localhost:4000') # Default LiteLLM proxy port
LITELLM_PROXY_API_KEY = os.getenv('LITELLM_PROXY_API_KEY') # Optional API key for securing the proxy
LLM_REFRESH_INTERVAL_SECONDS = int(os.getenv('LLM_REFRESH_INTERVAL_SECONDS', '3600')) # Default 1 hour
LLM_CACHE_TTL_SECONDS = int(os.getenv('LLM_CACHE_TTL_SECONDS', '3700')) # Slightly longer than refresh
FALLBACK_MODELS_JSON = os.getenv('FALLBACK_MODELS_JSON', '[]') # Default to an empty JSON array string

logger.info(f"LITELLM_PROXY_URL: {LITELLM_PROXY_URL}")
logger.info(f"LITELLM_PROXY_API_KEY loaded: {'Yes' if LITELLM_PROXY_API_KEY else 'No'}")
logger.info(f"LLM_REFRESH_INTERVAL_SECONDS: {LLM_REFRESH_INTERVAL_SECONDS}")
logger.info(f"LLM_CACHE_TTL_SECONDS: {LLM_CACHE_TTL_SECONDS}")
logger.info(f"FALLBACK_MODELS_JSON (first 50 chars): {FALLBACK_MODELS_JSON[:50]}...")

# Default model IDs for specific tasks (to be used with LLM Registry)
DEFAULT_EMBEDDING_MODEL_ID = os.getenv('DEFAULT_EMBEDDING_MODEL_ID', 'openai/text-embedding-ada-002')
DEFAULT_ANALYSIS_MODEL_ID = os.getenv('DEFAULT_ANALYSIS_MODEL_ID', 'openai/gpt-4o-mini')
DEFAULT_TRANSCRIPTION_MODEL_ID = os.getenv('DEFAULT_TRANSCRIPTION_MODEL_ID', 'groq/whisper-large-v3-turbo') # Example, user might prefer local

logger.info(f"DEFAULT_EMBEDDING_MODEL_ID: {DEFAULT_EMBEDDING_MODEL_ID}")
logger.info(f"DEFAULT_ANALYSIS_MODEL_ID: {DEFAULT_ANALYSIS_MODEL_ID}")
logger.info(f"DEFAULT_TRANSCRIPTION_MODEL_ID: {DEFAULT_TRANSCRIPTION_MODEL_ID}")


# It's good practice to ensure API keys are set if a model requiring one is selected by the application.
# However, crawl4ai handles API key loading from env vars internally if not passed.
# This config primarily serves to inform the frontend/user and provide defaults.
# The actual enforcement or requirement check might happen closer to the crawl4ai call.
