#!/usr/bin/env python3
"""
Quick test script for the Dynamic AI Insurance Query System
"""

import requests
import json

def test_server():
    """Test the server endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Dynamic AI Insurance Query System")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        print("\n1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {health_data['status']}")
            print(f"   Fuzzy matching: {'✅' if health_data['fuzzy_matching'] else '❌'}")
            print(f"   Gemini AI: {'✅' if health_data['gemini_ai'] else '❌'}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure the server is running with start_server_simple.bat")
        return False
    
    # Test 2: Query processing (with mock document)
    try:
        print("\n2️⃣ Testing query processing...")
        query_data = {
            "query": "IVF treatment, policy active 2 years",
            "file_id": ""  # Use default mock document
        }
        
        response = requests.post(
            f"{base_url}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query processing successful!")
            print(f"   Decision: {result['decision']}")
            print(f"   Confidence: {result['confidence']}%")
            print(f"   Reasoning: {result['justification']['reasoning']}")
            if result.get('amount'):
                print(f"   Amount: ₹{result['amount']:,}")
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Query test failed: {e}")
    
    # Test 3: IVF-friendly document test
    try:
        print("\n3️⃣ Testing IVF-friendly document...")
        query_data = {
            "query": "IVF treatment, 30F, policy active 2 years",
            "file_id": "ivf_friendly_doc"  # Use IVF-friendly mock
        }
        
        response = requests.post(
            f"{base_url}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ IVF-friendly test successful!")
            print(f"   Decision: {result['decision']}")
            print(f"   Confidence: {result['confidence']}%")
            print(f"   Amount: ₹{result.get('amount', 0):,}")
        else:
            print(f"❌ IVF-friendly test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ IVF-friendly test failed: {e}")
    
    print("\n🎯 Test completed!")
    print(f"📱 Frontend available at: {base_url}")
    print(f"🔧 API endpoints at: {base_url}/health, {base_url}/query")

if __name__ == "__main__":
    test_server()
