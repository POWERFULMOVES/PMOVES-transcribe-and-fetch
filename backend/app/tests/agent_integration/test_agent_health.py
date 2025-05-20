import requests

def test_health(url="http://localhost:8001/health"):
    try:
        resp = requests.get(url, timeout=5)
        assert resp.status_code == 200
        print("[PASS] Agent health endpoint:", resp.json())
    except Exception as e:
        print("[FAIL] Agent health endpoint:", e)

if __name__ == "__main__":
    test_health() 