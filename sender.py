import requests

SERVER_URL = "https://your-render-url.onrender.com/log"

def send_log(data):
    try:
        response = requests.post(SERVER_URL, json=data, timeout=10)
        print("✅ Log sent to server:", response.status_code)
        print("Response:", response.text)
    except Exception as e:
        print("❌ Failed to send log:", e)
