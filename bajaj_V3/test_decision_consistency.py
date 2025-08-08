#!/usr/bin/env python3
"""
Test script to verify the AI Insurance Query System decision consistency
"""

import requests
import json

API_BASE = 'http://localhost:5000'

def test_query(query_text, expected_decision=None):
    """Test a single query and return results"""
    print(f"\n🧪 Testing: '{query_text}'")
    
    try:
        response = requests.post(f'{API_BASE}/query', json={
            'query': query_text,
            'file_id': ''
        })
        
        if response.status_code == 200:
            data = response.json()
            decision = data.get('decision')
            confidence = data.get('confidence')
            reason = data.get('justification', {}).get('reasoning', data.get('reason', ''))
            
            print(f"   Decision: {decision} ({confidence}% confidence)")
            print(f"   Reason: {reason}")
            
            if expected_decision and decision != expected_decision:
                print(f"   ❌ MISMATCH! Expected {expected_decision}, got {decision}")
                return False
            else:
                print(f"   ✅ Result: {decision}")
                return True
        else:
            print(f"   ❌ ERROR: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ CONNECTION ERROR: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🎯 AI Insurance Query System - Decision Consistency Test")
    print("=" * 60)
    
    # Check server health
    try:
        response = requests.get(f'{API_BASE}/health')
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Server Status: {health.get('status')}")
            print(f"🔧 Server Mode: {health.get('server_mode')}")
            print(f"📄 Documents: {health.get('uploaded_documents', 0)}")
        else:
            print("❌ Server not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running at http://localhost:5000")
        return
    
    print("\n📋 TEST CASES")
    print("-" * 40)
    
    # Test cases with expected outcomes based on the balanced mock policy
    test_cases = [
        # These should be APPROVED (covered procedures)
        ("IVF treatment for 30-year-old woman, policy active for 3 years", "APPROVED"),
        ("Heart surgery for 45-year-old male", "APPROVED"),
        ("Cancer chemotherapy treatment", "APPROVED"),
        ("Emergency surgery after accident", "APPROVED"),
        ("Cardiac surgery for 50-year-old patient", "APPROVED"),
        ("General medical treatment", "APPROVED"),
        
        # These should consider waiting periods
        ("IVF treatment for 25-year-old female, policy active for 1 year", "REJECTED"),  # Waiting period
        ("Maternity care, policy held for 1 year", "REJECTED"),  # Waiting period
        
        # These should be REJECTED (exclusions)
        ("Cosmetic surgery for beauty enhancement", "REJECTED"),
        ("Experimental gene therapy", "REJECTED"),
        ("Vision correction surgery", "REJECTED"),
        
        # Edge cases
        ("Dental emergency treatment", "APPROVED"),  # Emergency dental is covered
        ("Dental implants for cosmetic purposes", "REJECTED"),  # Non-emergency dental implants excluded
    ]
    
    results = []
    for query, expected in test_cases:
        result = test_query(query, expected)
        results.append((query, expected, result))
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, _, result in results if result)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} tests")
    
    if passed < total:
        print(f"❌ Failed: {total - passed} tests")
        print("\nFailed tests:")
        for query, expected, result in results:
            if not result:
                print(f"  - '{query}' (expected {expected})")
    else:
        print("🎉 All tests passed! System is working correctly.")
    
    print("\n🔧 CONSISTENCY CHECK")
    print("-" * 40)
    
    # Test the same query multiple times to check consistency
    consistency_query = "IVF treatment for 30-year-old woman, policy active for 3 years"
    print(f"Testing consistency with: '{consistency_query}'")
    
    decisions = []
    for i in range(3):
        print(f"  Run {i+1}:", end=" ")
        response = requests.post(f'{API_BASE}/query', json={
            'query': consistency_query,
            'file_id': ''
        })
        
        if response.status_code == 200:
            decision = response.json().get('decision')
            decisions.append(decision)
            print(decision)
        else:
            print("ERROR")
    
    if len(set(decisions)) == 1:
        print(f"✅ Consistent results: All returned {decisions[0]}")
    else:
        print(f"❌ Inconsistent results: {decisions}")
    
    print(f"\n🎯 Test completed. Server mode should show balanced coverage behavior.")

if __name__ == "__main__":
    main()
