#!/usr/bin/env python3
"""
Test script for HackRx webhook endpoint
Tests the /hackrx/run endpoint with various request types
"""

import requests
import json
import time

# Configuration
LOCAL_URL = "http://localhost:5000/hackrx/run"
DEPLOYED_URL = "https://bajaj-insurance-engine.vercel.app/hackrx/run"

def test_hackrx_endpoint(base_url):
    """Test the HackRx webhook endpoint"""
    
    print(f"\n{'='*60}")
    print(f"Testing HackRx Webhook: {base_url}")
    print(f"{'='*60}\n")
    
    # Test 1: GET request (Health Check)
    print("Test 1: Health Check (GET request)")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Capabilities: {json.dumps(data.get('capabilities', {}), indent=2)}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "-"*40 + "\n")
    
    # Test 2: Simple Query
    print("Test 2: Simple Insurance Query")
    test_query = {
        "query": "25F with 2 years policy, need IVF treatment"
    }
    try:
        response = requests.post(base_url, json=test_query, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query processed successfully")
            print(f"   Decision: {data.get('decision')}")
            print(f"   Amount: ₹{data.get('amount', 0):,}")
            print(f"   Justification: {data.get('justification')}")
            print(f"   Confidence: {data.get('confidence')}%")
            print(f"   Classification: {data.get('confusion_matrix')}")
        else:
            print(f"❌ Query failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "-"*40 + "\n")
    
    # Test 3: Multiple Test Cases
    print("Test 3: Multiple Test Cases")
    test_request = {
        "type": "test",
        "test_cases": [
            {"query": "45M requiring cardiac surgery"},
            {"query": "30F pregnant, maternity benefits?"},
            {"query": "Emergency treatment coverage"}
        ]
    }
    try:
        response = requests.post(base_url, json=test_request, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test cases executed successfully")
            print(f"   Tests run: {data.get('tests_run')}")
            results = data.get('results', [])
            for i, result in enumerate(results, 1):
                print(f"\n   Test {i}: {result['test']}")
                print(f"   → Decision: {result['result']['decision']}")
                print(f"   → Amount: ₹{result['result']['amount']:,}")
        else:
            print(f"❌ Test execution failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "-"*40 + "\n")
    
    # Test 4: Policy Upload
    print("Test 4: Policy Upload Simulation")
    policy_request = {
        "type": "policy_upload",
        "policy_text": """
        Coverage Details:
        Cardiac Surgery: ₹1000000
        Emergency Treatment: ₹100000
        Maternity Benefits: ₹200000
        
        Exclusions:
        IVF treatment not covered
        Cosmetic surgery excluded
        """,
        "policy_type": "premium"
    }
    try:
        response = requests.post(base_url, json=policy_request, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Policy upload processed")
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Inclusions found: {data.get('inclusions_found')}")
            print(f"   Exclusions found: {data.get('exclusions_found')}")
            
            # Test query with uploaded policy
            if data.get('session_id'):
                print("\n   Testing query with uploaded policy...")
                query_with_policy = {
                    "query": "Need cardiac surgery",
                    "session_id": data.get('session_id')
                }
                response2 = requests.post(base_url, json=query_with_policy, timeout=10)
                if response2.status_code == 200:
                    result = response2.json()
                    print(f"   → Decision: {result.get('decision')}")
                    print(f"   → Amount: ₹{result.get('amount', 0):,}")
        else:
            print(f"❌ Policy upload failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60 + "\n")

def main():
    """Main test function"""
    print("\n🏆 HackRx Webhook Endpoint Test Suite")
    print("=====================================\n")
    
    # Choose which URL to test
    print("Select testing option:")
    print("1. Test LOCAL endpoint (http://localhost:5000)")
    print("2. Test DEPLOYED endpoint (Vercel)")
    print("3. Test BOTH endpoints")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        print("\nTesting LOCAL endpoint...")
        print("Make sure your server is running: python api/hackrx.py")
        input("Press Enter when ready...")
        test_hackrx_endpoint(LOCAL_URL)
        
    elif choice == "2":
        print("\nTesting DEPLOYED endpoint...")
        print("Make sure your app is deployed to Vercel")
        deployed_url = input(f"Enter your deployed URL (or press Enter for default): ").strip()
        if not deployed_url:
            deployed_url = DEPLOYED_URL
        else:
            if not deployed_url.endswith("/hackrx/run"):
                deployed_url = deployed_url.rstrip("/") + "/hackrx/run"
        test_hackrx_endpoint(deployed_url)
        
    elif choice == "3":
        print("\nTesting BOTH endpoints...")
        print("Testing LOCAL first...")
        test_hackrx_endpoint(LOCAL_URL)
        print("\nTesting DEPLOYED...")
        test_hackrx_endpoint(DEPLOYED_URL)
    
    else:
        print("Invalid choice. Please run again and select 1, 2, or 3.")
    
    print("\n✅ Testing complete!")
    
    # Show webhook URL for submission
    print("\n" + "="*60)
    print("📋 WEBHOOK URL FOR HACKRX SUBMISSION:")
    print("="*60)
    print("\nAfter deployment, your webhook URL will be:")
    print(f"\n   https://your-project-name.vercel.app/hackrx/run")
    print(f"\nExample:")
    print(f"   https://bajaj-insurance-engine.vercel.app/hackrx/run")
    print("\nThis URL will:")
    print("✅ Accept GET requests for health checks")
    print("✅ Accept POST requests with insurance queries")
    print("✅ Return JSON responses with decisions")
    print("✅ Handle test cases from HackRx evaluation")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
