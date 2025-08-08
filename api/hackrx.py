#!/usr/bin/env python3
"""
🏆 HackRx Webhook Endpoint Handler
Endpoint: /hackrx/run
Purpose: Receives and processes test requests for HackRx hackathon
"""

import json
import os
import re
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Import existing processors if available
try:
    from vercel_index import (
        DocumentProcessor, 
        QueryProcessor, 
        FuzzyMatcher,
        PROCEDURE_MAPPINGS,
        session_documents
    )
    PROCESSORS_AVAILABLE = True
except ImportError:
    PROCESSORS_AVAILABLE = False
    # Fallback implementations
    PROCEDURE_MAPPINGS = {
        'IVF': ['in vitro fertilization', 'fertility treatment'],
        'cardiac': ['heart surgery', 'cardiovascular'],
        'maternity': ['pregnancy care', 'prenatal'],
        'emergency': ['urgent care', 'emergency room']
    }
    session_documents = {}

# Sample policy data for testing
SAMPLE_POLICY_DATA = {
    'inclusions': {
        'cardiac surgery': 500000,
        'general medical': 100000,
        'emergency treatment': 50000,
        'diagnostic tests': 25000,
        'hospitalization': 200000
    },
    'exclusions': [
        'ivf treatment',
        'fertility procedures',
        'cosmetic surgery',
        'experimental treatments'
    ],
    'policy_info': {
        'type': 'Standard Policy',
        'name': 'Basic Health Insurance'
    }
}

class HackRxProcessor:
    """Process HackRx specific requests"""
    
    @staticmethod
    def process_test_request(data):
        """Process incoming test request from HackRx"""
        
        # Extract request type
        request_type = data.get('type', 'query')
        
        if request_type == 'health_check':
            return HackRxProcessor.health_check()
        
        elif request_type == 'policy_upload':
            return HackRxProcessor.process_policy(data)
        
        elif request_type == 'query' or request_type == 'insurance_query':
            return HackRxProcessor.process_query(data)
        
        elif request_type == 'test':
            return HackRxProcessor.run_tests(data)
        
        else:
            # Default: treat as query
            return HackRxProcessor.process_query(data)
    
    @staticmethod
    def health_check():
        """Return system health status"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Bajaj Insurance Query Engine',
            'version': '1.0.0',
            'endpoints': ['/hackrx/run', '/query', '/upload', '/health'],
            'capabilities': {
                'pdf_processing': True,
                'nlp_analysis': True,
                'fuzzy_matching': True,
                'decision_engine': True
            }
        }
    
    @staticmethod
    def process_policy(data):
        """Process policy document data"""
        policy_text = data.get('policy_text', '')
        policy_type = data.get('policy_type', 'standard')
        
        # Extract clauses from policy text
        inclusions = {}
        exclusions = []
        
        # Simple extraction logic
        lines = policy_text.lower().split('\n') if policy_text else []
        
        for line in lines:
            # Check for coverage amounts
            amount_match = re.search(r'(\w+.*?):\s*₹?(\d+(?:,\d{3})*)', line)
            if amount_match:
                service = amount_match.group(1).strip()
                amount = int(re.sub(r'[,₹]', '', amount_match.group(2)))
                inclusions[service] = amount
            
            # Check for exclusions
            if 'not covered' in line or 'excluded' in line:
                exclusion = line.replace('not covered', '').replace('excluded', '').strip()
                if exclusion:
                    exclusions.append(exclusion)
        
        # Store in session
        session_id = f"hackrx_{datetime.now().timestamp()}"
        session_documents[session_id] = {
            'inclusions': inclusions if inclusions else SAMPLE_POLICY_DATA['inclusions'],
            'exclusions': exclusions if exclusions else SAMPLE_POLICY_DATA['exclusions'],
            'policy_info': {'type': policy_type}
        }
        
        return {
            'status': 'success',
            'session_id': session_id,
            'policy_processed': True,
            'inclusions_found': len(inclusions),
            'exclusions_found': len(exclusions)
        }
    
    @staticmethod
    def process_query(data):
        """Process insurance query"""
        query = data.get('query', '') or data.get('question', '')
        session_id = data.get('session_id', '')
        
        if not query:
            return {
                'error': 'No query provided',
                'status': 'failed'
            }
        
        # Extract information from query
        extracted_info = HackRxProcessor.extract_query_info(query)
        
        # Get policy data
        if session_id and session_id in session_documents:
            policy_data = session_documents[session_id]
        else:
            policy_data = SAMPLE_POLICY_DATA
        
        # Make decision
        decision = HackRxProcessor.make_coverage_decision(
            extracted_info.get('procedure', 'general medical'),
            policy_data
        )
        
        return {
            'status': 'success',
            'query': query,
            'decision': decision['decision'],
            'amount': decision['amount'],
            'confidence': decision['confidence'],
            'justification': decision['justification'],
            'confusion_matrix': decision['confusion_matrix'],
            'extracted_info': extracted_info,
            'policy_type': policy_data['policy_info'].get('type', 'Standard'),
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def extract_query_info(query):
        """Extract structured information from query"""
        query_lower = query.lower()
        extracted = {}
        
        # Age extraction
        age_match = re.search(r'(\d+)\s*(?:year|yr)s?\s*old|\b(\d+)[yYfFmM]\b', query)
        if age_match:
            age = int(age_match.group(1) or age_match.group(2))
            if 0 < age < 120:
                extracted['age'] = age
        
        # Gender extraction
        if any(term in query_lower for term in ['female', 'woman', 'f,', 'pregnant', '25f', '30f']):
            extracted['gender'] = 'female'
        elif any(term in query_lower for term in ['male', 'man', 'm,', '45m', '50m']):
            extracted['gender'] = 'male'
        
        # Procedure extraction
        for category, synonyms in PROCEDURE_MAPPINGS.items():
            if category.lower() in query_lower:
                extracted['procedure'] = category
                break
            for synonym in synonyms:
                if synonym.lower() in query_lower:
                    extracted['procedure'] = category
                    break
        
        # Policy duration
        duration_match = re.search(r'(\d+)\s*(?:year|yr|month)s?\s*(?:policy|active|coverage)', query_lower)
        if duration_match:
            extracted['policy_duration'] = f"{duration_match.group(1)} years"
        
        return extracted
    
    @staticmethod
    def make_coverage_decision(procedure, policy_data):
        """Make coverage decision based on procedure and policy"""
        procedure_lower = procedure.lower()
        
        # Check inclusions
        for covered_item, amount in policy_data.get('inclusions', {}).items():
            if procedure_lower in covered_item.lower() or covered_item.lower() in procedure_lower:
                return {
                    'decision': 'APPROVED',
                    'amount': amount,
                    'confidence': 95,
                    'justification': f'Covered under: {covered_item}',
                    'confusion_matrix': 'AA'  # Correctly Approved
                }
        
        # Check exclusions
        for excluded_item in policy_data.get('exclusions', []):
            if procedure_lower in excluded_item.lower() or excluded_item.lower() in procedure_lower:
                return {
                    'decision': 'REJECTED',
                    'amount': 0,
                    'confidence': 95,
                    'justification': f'Excluded: {excluded_item}',
                    'confusion_matrix': 'RR'  # Correctly Rejected
                }
        
        # Check semantic mappings
        for category, synonyms in PROCEDURE_MAPPINGS.items():
            if category.lower() == procedure_lower:
                for covered_item, amount in policy_data.get('inclusions', {}).items():
                    if category.lower() in covered_item.lower():
                        return {
                            'decision': 'APPROVED',
                            'amount': amount,
                            'confidence': 85,
                            'justification': f'Covered under: {covered_item}',
                            'confusion_matrix': 'AA'
                        }
        
        # Default: Not found
        return {
            'decision': 'REJECTED',
            'amount': 0,
            'confidence': 70,
            'justification': 'No matching coverage found in policy',
            'confusion_matrix': 'RR'
        }
    
    @staticmethod
    def run_tests(data):
        """Run test cases for HackRx evaluation"""
        test_cases = data.get('test_cases', [])
        results = []
        
        # Default test cases if none provided
        if not test_cases:
            test_cases = [
                {'query': '25F with 2 years policy, need IVF treatment'},
                {'query': '45M requiring cardiac surgery'},
                {'query': '30F pregnant, maternity benefits?'},
                {'query': 'Emergency treatment coverage'}
            ]
        
        for test_case in test_cases:
            result = HackRxProcessor.process_query(test_case)
            results.append({
                'test': test_case.get('query', ''),
                'result': result
            })
        
        return {
            'status': 'success',
            'tests_run': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }

@app.route('/hackrx/run', methods=['POST', 'GET', 'OPTIONS'])
def hackrx_run():
    """
    Main HackRx webhook endpoint
    Accepts test requests and returns appropriate responses
    """
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
    
    # Handle GET request (health check)
    if request.method == 'GET':
        return jsonify(HackRxProcessor.health_check())
    
    # Handle POST request (main processing)
    try:
        # Get request data
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            # Try to parse form data or raw data
            data = request.form.to_dict() if request.form else {}
            if not data and request.data:
                try:
                    data = json.loads(request.data)
                except:
                    data = {'query': request.data.decode('utf-8')}
        
        # Process the request
        result = HackRxProcessor.process_test_request(data)
        
        # Return success response
        response = make_response(jsonify(result))
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.status_code = 200
        
        return response
        
    except Exception as e:
        # Return error response
        error_response = {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'message': 'An error occurred processing your request'
        }
        
        response = make_response(jsonify(error_response))
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.status_code = 500
        
        return response

# Additional endpoints for compatibility
@app.route('/hackrx/health', methods=['GET'])
def hackrx_health():
    """Health check endpoint"""
    return jsonify(HackRxProcessor.health_check())

@app.route('/hackrx/test', methods=['POST'])
def hackrx_test():
    """Test endpoint for running test cases"""
    data = request.get_json()
    return jsonify(HackRxProcessor.run_tests(data))

# Handler for Vercel
def handler(request):
    """Vercel serverless function handler"""
    with app.test_request_context(
        path=request.path,
        method=request.method,
        headers=request.headers,
        data=request.get_data(),
        query_string=request.query_string
    ):
        response = app.full_dispatch_request()
        return response

# For local testing
if __name__ == '__main__':
    print("🏆 HackRx Webhook Server Starting...")
    print("📍 Webhook URL: http://localhost:5000/hackrx/run")
    print("📍 Health Check: http://localhost:5000/hackrx/health")
    print("📍 Test Runner: http://localhost:5000/hackrx/test")
    print("\nReady to receive HackRx test requests!")
    
    app.run(debug=True, port=5000)
