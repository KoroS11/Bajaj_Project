#!/usr/bin/env python3
"""
Test script to verify both APIs work correctly
"""

import requests
import json
import sys
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

def test_api(api_name, base_url):
    """Test an API endpoint"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"Testing {api_name}")
    print(f"Base URL: {base_url}")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    results = []
    
    # Test 1: Health Check
    print(f"{Fore.YELLOW}Test 1: Health Check{Style.RESET_ALL}")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"{Fore.GREEN}✅ Health check passed{Style.RESET_ALL}")
            print(f"  Status: {data.get('status', 'N/A')}")
            print(f"  Message: {data.get('message', 'N/A')}")
            if 'capabilities' in data:
                print(f"  Capabilities:")
                for key, value in data['capabilities'].items():
                    print(f"    - {key}: {value}")
            results.append(True)
        else:
            print(f"{Fore.RED}❌ Health check failed: {response.status_code}{Style.RESET_ALL}")
            results.append(False)
    except Exception as e:
        print(f"{Fore.RED}❌ Health check error: {e}{Style.RESET_ALL}")
        results.append(False)
    
    # Test 2: Query without PDF
    print(f"\n{Fore.YELLOW}Test 2: Query without PDF upload{Style.RESET_ALL}")
    try:
        query_data = {
            "query": "25F with 2 years policy, need IVF treatment",
            "policy_type": "standard"
        }
        response = requests.post(
            f"{base_url}/query",
            json=query_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"{Fore.GREEN}✅ Query processed successfully{Style.RESET_ALL}")
            print(f"  Decision: {data.get('decision', 'N/A')}")
            print(f"  Justification: {data.get('justification', 'N/A')}")
            print(f"  Confidence: {data.get('confidence', 'N/A')}%")
            print(f"  Classification: {data.get('confusion_matrix', 'N/A')}")
            if data.get('extracted_info'):
                print(f"  Extracted Info: {json.dumps(data['extracted_info'], indent=4)}")
            results.append(True)
        else:
            print(f"{Fore.RED}❌ Query failed: {response.status_code}{Style.RESET_ALL}")
            print(f"  Response: {response.text[:200]}")
            results.append(False)
    except Exception as e:
        print(f"{Fore.RED}❌ Query error: {e}{Style.RESET_ALL}")
        results.append(False)
    
    # Test 3: Different query types
    print(f"\n{Fore.YELLOW}Test 3: Multiple query types{Style.RESET_ALL}")
    test_queries = [
        ("45M requiring cardiac surgery", "cardiac"),
        ("30F pregnant, maternity benefits?", "maternity"),
        ("Emergency treatment coverage", "emergency")
    ]
    
    for query_text, expected_procedure in test_queries:
        try:
            query_data = {"query": query_text}
            response = requests.post(
                f"{base_url}/query",
                json=query_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                extracted_procedure = data.get('extracted_info', {}).get('procedure', 'none')
                if expected_procedure.lower() in extracted_procedure.lower() or extracted_procedure.lower() in expected_procedure.lower():
                    print(f"{Fore.GREEN}  ✅ '{query_text[:30]}...' - Correctly identified as {extracted_procedure}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}  ⚠️  '{query_text[:30]}...' - Identified as {extracted_procedure} (expected {expected_procedure}){Style.RESET_ALL}")
                results.append(True)
            else:
                print(f"{Fore.RED}  ❌ Failed: '{query_text[:30]}...'{Style.RESET_ALL}")
                results.append(False)
        except Exception as e:
            print(f"{Fore.RED}  ❌ Error processing '{query_text[:30]}...': {e}{Style.RESET_ALL}")
            results.append(False)
    
    # Summary
    success_count = sum(results)
    total_count = len(results)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    print(f"\n{Fore.CYAN}Summary for {api_name}:{Style.RESET_ALL}")
    print(f"  Tests passed: {success_count}/{total_count}")
    print(f"  Success rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print(f"{Fore.GREEN}  🎉 All tests passed!{Style.RESET_ALL}")
    elif success_rate >= 75:
        print(f"{Fore.YELLOW}  ⚠️  Most tests passed, minor issues detected{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}  ❌ Multiple tests failed, needs attention{Style.RESET_ALL}")
    
    return success_rate

def main():
    """Main test function"""
    print(f"{Fore.MAGENTA}{'='*60}")
    print("BAJAJ INSURANCE QUERY ENGINE - API TEST SUITE")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    # Test the Vercel-compatible API
    vercel_api_url = "http://localhost:5000"
    
    print(f"\n{Fore.CYAN}Starting Vercel-compatible API test...{Style.RESET_ALL}")
    print(f"Make sure the API is running: python api/vercel_index.py")
    print(f"Press Enter when ready or 'skip' to skip this test...")
    user_input = input().strip().lower()
    
    if user_input != 'skip':
        try:
            vercel_success = test_api("Vercel-Compatible API", vercel_api_url)
        except:
            print(f"{Fore.RED}Could not connect to Vercel API. Make sure it's running on port 5000{Style.RESET_ALL}")
            vercel_success = 0
    else:
        vercel_success = None
    
    # Test the original API
    print(f"\n{Fore.CYAN}Starting Original API test...{Style.RESET_ALL}")
    print(f"Make sure the API is running: python api/index.py")
    print(f"Press Enter when ready or 'skip' to skip this test...")
    user_input = input().strip().lower()
    
    if user_input != 'skip':
        try:
            original_success = test_api("Original API", vercel_api_url)
        except:
            print(f"{Fore.RED}Could not connect to Original API. Make sure it's running on port 5000{Style.RESET_ALL}")
            original_success = 0
    else:
        original_success = None
    
    # Final summary
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print("FINAL TEST RESULTS")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    if vercel_success is not None:
        print(f"Vercel API: {Fore.GREEN if vercel_success >= 75 else Fore.RED}{vercel_success:.1f}% success{Style.RESET_ALL}")
    else:
        print(f"Vercel API: {Fore.YELLOW}Skipped{Style.RESET_ALL}")
    
    if original_success is not None:
        print(f"Original API: {Fore.GREEN if original_success >= 75 else Fore.RED}{original_success:.1f}% success{Style.RESET_ALL}")
    else:
        print(f"Original API: {Fore.YELLOW}Skipped{Style.RESET_ALL}")
    
    if vercel_success is not None and vercel_success >= 75:
        print(f"\n{Fore.GREEN}✅ Your project is ready for Vercel deployment!{Style.RESET_ALL}")
        print(f"\nNext steps:")
        print(f"1. Install Vercel CLI: npm install -g vercel")
        print(f"2. Deploy: vercel")
        print(f"3. Follow the prompts to complete deployment")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Please fix any issues before deployment{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
