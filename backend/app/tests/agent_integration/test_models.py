import yaml
import sys
import requests


def load_config(path=".env.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def test_model(model_name, litellm_url):
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": f"Say hello from {model_name}"}]
    }
    try:
        resp = requests.post(f"{litellm_url}/v1/chat/completions", json=payload, timeout=20)
        resp.raise_for_status()
        print(f"[PASS] {model_name}: {resp.json()['choices'][0]['message']['content']}")
    except Exception as e:
        print(f"[FAIL] {model_name}: {e}")

if __name__ == "__main__":
    config = load_config()
    litellm_url = config.get("litellm", {}).get("proxy_url", "http://localhost:4000")
    models = config.get("pipecat", {}).get("models", [])
    if not models:
        print("No models listed in .env.yaml under pipecat.models")
        sys.exit(1)
    for model in models:
        test_model(model, litellm_url) 