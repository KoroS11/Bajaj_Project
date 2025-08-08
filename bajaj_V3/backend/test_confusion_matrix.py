#!/usr/bin/env python3
"""
🎯 Confusion Matrix Test Script
Tests all 4 confusion matrix cases:
- AA (True Positive): Should approve & system approves
- RR (True Negative): Should reject & system rejects  
- AR (False Negative): Should approve but system rejects
- RA (False Positive): Should reject but system approves
"""

import requests
import json
import time

# Test server URL
BASE_URL = "http://localhost:5000"

def test_confusion_matrix():
    """Test all confusion matrix scenarios"""
    
    print("🎯 CONFUSION MATRIX TEST SUITE")
    print("=" * 50)
    
    test_cases = [
        {
            'name': 'AA - True Positive (Correct Approval)',
            'query': 'Heart surgery for 45-year-old male',
            'file_id': 'mock_document',
            'expected': 'APPROVED',
            'actual_outcome': 'APPROVED'
        },
        {
            'name': 'RR - True Negative (Correct Rejection)',
            'query': 'IVF treatment, policy active 2 years',
            'file_id': 'mock_document',
            'expected': 'REJECTED',
            'actual_outcome': 'REJECTED'
        },
        {
            'name': 'AR - False Negative (Should approve but rejects)',
            'query': 'IVF treatment, policy active 2 years',
            'file_id': 'ivf_friendly_doc',
            'expected': 'APPROVED',
            'actual_outcome': 'APPROVED'
        },
        {
            'name': 'RA - False Positive (Should reject but approves)', 
            'query': 'Cardiac surgery emergency',
            'file_id': 'mock_document',
            'expected': 'REJECTED',
            'actual_outcome': 'APPROVED'
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test['name']}")
        print(f"Query: '{test['query']}'")
        print(f"Document: {test['file_id']}")
        print(f"Expected: {test['expected']}")
        
        try:
            # Make request to query endpoint
            payload = {
                'query': test['query'],
                'file_id': test['file_id'],
                'actual_outcome': test['actual_outcome']
            }
            
            response = requests.post(f"{BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                decision = data.get('decision')
                confidence = data.get('confidence', 0)
                confusion_matrix = data.get('confusion_matrix', 'Not classified')
                
                print(f"System Decision: {decision}")
                print(f"Confidence: {confidence}%")
                print(f"Confusion Matrix: {confusion_matrix}")
                
                # Determine if test passed
                test_passed = decision == test['expected']
                print(f"✅ PASS" if test_passed else "❌ FAIL")
                
                results.append({
                    'test': test['name'],
                    'passed': test_passed,
                    'decision': decision,
                    'expected': test['expected'],
                    'confidence': confidence,
                    'confusion_matrix': confusion_matrix
                })
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                results.append({
                    'test': test['name'],
                    'passed': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            results.append({
                'test': test['name'],
                'passed': False,
                'error': str(e)
            })
        
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r.get('passed', False))
    total = len(results)
    
    for result in results:
        status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
        print(f"{status} {result['test']}")
        if 'error' in result:
            print(f"    Error: {result['error']}")
        elif 'confusion_matrix' in result:
            print(f"    Matrix: {result['confusion_matrix']}")
    
    print(f"\n🎯 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    return results

def test_fuzzy_matching():
    """Test fuzzy matching capabilities"""
    
    print("\n🧠 FUZZY MATCHING TEST")
    print("=" * 30)
    
    test_queries = [
        "fertility consultation",  # Should match IVF exclusions
        "heart operation",         # Should match cardiac surgery
        "prenatal checkup",        # Should match maternity care
        "cancer therapy",          # Should match cancer treatment
        "emergency treatment"      # Should match emergency care
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        
        try:
            payload = {'query': query, 'file_id': 'mock_document'}
            response = requests.post(f"{BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                entities = data.get('entities_extracted', {})
                fuzzy_terms = data.get('fuzzy_matched_terms', [])
                
                print(f"   Procedure detected: {entities.get('procedure_type', 'None')}")
                print(f"   Match confidence: {entities.get('match_confidence', 0)}%")
                print(f"   Fuzzy matched terms: {fuzzy_terms}")
                print(f"   Decision: {data.get('decision')}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Confusion Matrix Tests...")
    print("Make sure the server is running on http://localhost:5000")
    
    try:
        # Test server health
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            
            # Run confusion matrix tests
            test_confusion_matrix()
            
            # Run fuzzy matching tests
            test_fuzzy_matching()
            
        else:
            print("❌ Server health check failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first:")
        print("   python main_intelligent_fuzzy.py")
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
