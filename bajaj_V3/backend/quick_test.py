import requests
import time

def test_server():
    print("Testing server...")
    try:
        # Wait a moment for server to start
        time.sleep(2)
        
        # Test health endpoint
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            print("✅ Server is running!")
            print("🌐 Go to: http://localhost:5000")
            print("🧪 Testing query...")
            
            # Test query
            query_response = requests.post('http://localhost:5000/query', 
                json={'query': 'IVF treatment'})
            result = query_response.json()
            print(f"Decision: {result['decision']}")
            print(f"Reason: {result['reason']}")
        else:
            print("❌ Server not responding")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_server()
