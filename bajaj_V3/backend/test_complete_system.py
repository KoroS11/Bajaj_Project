#!/usr/bin/env python3
"""
Comprehensive test script for the Dynamic AI Insurance Query System
Tests both uploaded document processing and query evaluation
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:5000"

def test_server_health():
    """Test if server is running and get status"""
    print("🏥 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Server is healthy!")
            print(f"   Mode: {health_data.get('server_mode', 'Unknown')}")
            print(f"   Uploaded documents: {health_data.get('uploaded_documents', 0)}")
            print(f"   PDF processing: {'✅' if health_data.get('system_capabilities', {}).get('pdf_processing') else '❌'}")
            print(f"   Fuzzy matching: {'✅' if health_data.get('system_capabilities', {}).get('fuzzy_matching') else '❌'}")
            return True, health_data
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure to run: python main_intelligent_fuzzy.py")
        return False, None

def test_query_processing(query_text, expected_decision=None):
    """Test query processing"""
    print(f"\n🔍 Testing query: '{query_text}'")
    try:
        query_data = {
            "query": query_text,
            "file_id": ""  # Let system auto-select most recent document
        }
        
        response = requests.post(
            f"{BASE_URL}/query",
            json=query_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Decision: {result['decision']}")
            print(f"   Confidence: {result['confidence']}%")
            print(f"   Reasoning: {result['justification']['reasoning']}")
            print(f"   Document source: {result['document_info'].get('source', 'unknown')}")
            
            if result.get('amount'):
                print(f"   Coverage amount: ₹{result['amount']:,}")
            
            if result.get('fuzzy_matched_terms'):
                print(f"   Matched terms: {result['fuzzy_matched_terms']}")
            
            entities = result.get('entities_extracted', {})
            if entities:
                print(f"   Extracted entities: {entities}")
            
            # Check if decision matches expectation
            if expected_decision and result['decision'] != expected_decision:
                print(f"   ⚠️ Expected {expected_decision}, got {result['decision']}")
            else:
                print("   ✅ Query processed successfully")
            
            return True, result
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Query test failed: {e}")
        return False, None

def test_document_upload():
    """Test document upload if sample PDF exists"""
    print("\n📄 Testing document upload...")
    
    # Look for any PDF files in the uploads directory
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
        if pdf_files:
            print(f"   Found existing PDFs: {len(pdf_files)} files")
            return True
    
    print("   ℹ️ No test PDFs found - upload functionality available via web interface")
    return True

def run_comprehensive_tests():
    """Run all tests"""
    print("🧪 COMPREHENSIVE INSURANCE SYSTEM TEST")
    print("=" * 50)
    
    # Test 1: Server health
    server_ok, health_data = test_server_health()
    if not server_ok:
        return
    
    # Test 2: Document upload check
    test_document_upload()
    
    # Test 3: Various query types
    test_queries = [
        ("IVF treatment for 30-year-old woman", "Should be rejected in standard policy"),
        ("Heart surgery for cardiac patient", "Should be approved with high coverage"),
        ("Cancer chemotherapy treatment", "Should be approved with high coverage"),
        ("Emergency surgery after accident", "Should be approved for emergency coverage"),
        ("Prenatal checkup for pregnancy", "Should be approved for maternity care"),
        ("Dental implant surgery", "Should be rejected as cosmetic"),
        ("General medical consultation", "Should be approved under general coverage"),
        ("MRI scan for diagnosis", "Should be approved as diagnostic procedure")
    ]
    
    print(f"\n🎯 Testing {len(test_queries)} different query types...")
    
    successful_tests = 0
    for query, description in test_queries:
        print(f"\n{'='*60}")
        print(f"Test: {description}")
        success, result = test_query_processing(query)
        if success:
            successful_tests += 1
        time.sleep(1)  # Brief pause between tests
    
    # Test 4: Document listing
    print(f"\n📋 Testing document listing...")
    try:
        response = requests.get(f"{BASE_URL}/documents")
        if response.status_code == 200:
            docs = response.json()
            print(f"   ✅ Found {docs['uploaded_documents']} uploaded documents")
        else:
            print(f"   ❌ Document listing failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Document listing error: {e}")
    
    # Summary
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Successful query tests: {successful_tests}/{len(test_queries)}")
    print(f"🌐 Server accessible at: {BASE_URL}")
    print(f"📊 System mode: {health_data.get('server_mode', 'Unknown') if health_data else 'Unknown'}")
    
    if health_data and health_data.get('uploaded_documents', 0) > 0:
        print("🎉 System is using uploaded documents for decision making!")
    else:
        print("⚠️ System is using mock documents - upload a PDF for real document processing")
    
    print(f"\n💡 To upload documents and test queries:")
    print(f"   1. Open browser: {BASE_URL}")
    print(f"   2. Upload your insurance PDF")
    print(f"   3. Submit queries to test against your document")

if __name__ == "__main__":
    run_comprehensive_tests()
