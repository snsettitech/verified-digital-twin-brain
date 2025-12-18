import requests
import time
import os
import json
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
            f"{BASE_URL}/chat/{twin_id}",
            json={"query": query},
            headers=HEADERS
        )
        response.raise_for_status()
        
        # Read the stream
        print("Response received (streaming)...")
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                if data.get("type") == "content":
                    print(data.get("content"), end="", flush=True)
                elif data.get("type") == "metadata":
                    print(f"\n[Metadata] Confidence: {data.get('confidence_score')}")
        print("\nChat test completed!")
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
