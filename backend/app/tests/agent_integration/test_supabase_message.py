from supabase import create_client
import yaml
import time

def load_config(path=".env.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def test_supabase_message():
    config = load_config()
    supa = config["supabase"]
    url = supa.get("url", f"https://{supa['id']}.supabase.co")
    key = supa["key"]
    client = create_client(url, key)
    msg = {
        "session_id": "test-session",
        "message": {"type": "human", "content": "Hello from test script"}
    }
    resp = client.table("messages").insert(msg).execute()
    print("[INFO] Inserted test message, check agent logs for response.")
    time.sleep(2)  # Give agent time to process

if __name__ == "__main__":
    test_supabase_message() 