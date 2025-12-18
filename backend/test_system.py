import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"
DEV_TOKEN = "development_token"
HEADERS = {"Authorization": f"Bearer {DEV_TOKEN}"}

def test_health():
    print("Checking system health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"Health status: {data['status']}")
        for service, status in data['services'].items():
            print(f"  - {service}: {status}")
        return data['status'] == "online"
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_rag_pipeline():
    print("\nTesting RAG pipeline...")
    twin_id = "eeeed554-9180-4229-a9af-0f8dd2c69e9b"
    
    # 1. Ingest dummy content (In a real test, we'd upload a file, but here we can check the chat directly if content exists)
    # For a full integration test, we would need a small test PDF.
    
    # 2. Test Chat
    query = "Hello, what can you do?"
    print(f"Sending query: {query}")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/{twin_id}?query={query}",
            headers=HEADERS
        )
        response.raise_for_status()
        data = response.json()
        print("Response received!")
        print(f"Answer: {data['answer'][:100]}...")
        print(f"Confidence: {data.get('confidence_score', 0)}")
        print(f"Citations: {data.get('citations', [])}")
        return True
    except Exception as e:
        print(f"Chat test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Verified Digital Twin Brain - System Verification ===\n")
    if test_health():
        test_rag_pipeline()
    else:
        print("\nSkipping RAG tests because system is not healthy.")
