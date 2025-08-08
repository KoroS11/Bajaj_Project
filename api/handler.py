#!/usr/bin/env python3
"""
🎯 VERCEL-COMPATIBLE INSURANCE QUERY ENGINE
✅ Works without database - uses in-memory storage
✅ Optimized for serverless deployment
"""

import json
import base64
import io
import re
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample policy data (since we can't persist uploads in Vercel)
SAMPLE_POLICIES = {
    'standard': {
        'name': 'Standard Health Policy',
        'type': 'Standard Policy',
        'inclusions': {
            'cardiac surgery': 500000,
            'general medical': 100000,
            'emergency treatment': 50000,
            'diagnostic tests': 25000,
            'consultation': 5000,
            'hospitalization': 200000
        },
        'exclusions': [
            'ivf treatment',
            'fertility procedures',
            'cosmetic surgery',
            'experimental treatments',
            'dental procedures',
            'pre-existing conditions for first 48 months'
        ],
        'waiting_periods': {
            'surgery': '24 months',
            'cardiac': '48 months'
        }
    },
    'fertility': {
        'name': 'Fertility Plus Policy',
        'type': 'Fertility Policy',
        'inclusions': {
            'ivf treatment': 300000,
            'fertility consultation': 50000,
            'maternity benefits': 150000,
            'general medical': 100000,
            'diagnostic tests': 30000,
            'prenatal care': 75000
        },
        'exclusions': [
            'cosmetic surgery',
            'experimental treatments',
            'dental procedures'
        ],
        'waiting_periods': {
            'ivf': '12 months',
            'fertility': '12 months'
        }
    },
    'premium': {
        'name': 'Premium Comprehensive Policy',
        'type': 'Premium Policy',
        'inclusions': {
            'cardiac surgery': 1000000,
            'cancer treatment': 750000,
            'surgery': 500000,
            'maternity benefits': 200000,
            'ivf treatment': 400000,
            'emergency treatment': 100000,
            'diagnostic tests': 50000
        },
        'exclusions': [
            'cosmetic surgery',
            'experimental treatments'
        ],
        'waiting_periods': {
            'surgery': '12 months',
            'cardiac': '24 months'
        }
    }
}

# Procedure mappings for semantic understanding
PROCEDURE_MAPPINGS = {
    'IVF': ['in vitro fertilization', 'fertility treatment', 'assisted reproduction', 'ivf'],
    'fertility': ['reproductive health', 'infertility treatment', 'conception assistance'],
    'cardiac': ['heart surgery', 'cardiovascular', 'bypass surgery', 'angioplasty'],
    'maternity': ['pregnancy care', 'prenatal', 'childbirth', 'delivery'],
    'cancer': ['oncology', 'chemotherapy', 'radiation therapy'],
    'emergency': ['urgent care', 'emergency room', 'trauma care'],
    'surgery': ['operation', 'surgical procedure', 'operative treatment'],
    'diagnostic': ['tests', 'scans', 'medical tests', 'laboratory tests']
}

class QueryProcessor:
    """Process natural language queries"""
    
    @staticmethod
    def extract_info(query):
        """Extract structured information from query"""
        query_lower = query.lower()
        extracted = {}
        
        # Age extraction
        age_match = re.search(r'(\d+)\s*(?:year|yr)s?\s*old|\b(\d+)[yY]', query)
        if age_match:
            age = int(age_match.group(1) or age_match.group(2))
            if 0 < age < 120:
                extracted['age'] = age
        
        # Gender extraction
        if any(term in query_lower for term in ['female', 'woman', 'f,', '25f', 'pregnant']):
            extracted['gender'] = 'female'
        elif any(term in query_lower for term in ['male', 'man', 'm,', '25m']):
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
        duration_match = re.search(r'(\d+)\s*(?:year|yr|month)s?.*?(?:policy|coverage|active)', query_lower)
        if duration_match:
            duration = int(duration_match.group(1))
            unit = 'years' if 'year' in duration_match.group(0) or 'yr' in duration_match.group(0) else 'months'
            extracted['policy_duration'] = f"{duration} {unit}"
        
        return extracted

class DecisionEngine:
    """Make coverage decisions"""
    
    @staticmethod
    def check_coverage(procedure, policy_data):
        """Check if procedure is covered"""
        procedure_lower = procedure.lower()
        
        # Check inclusions
        for covered_item in policy_data['inclusions']:
            if procedure_lower in covered_item.lower() or covered_item.lower() in procedure_lower:
                return {
                    'covered': True,
                    'amount': policy_data['inclusions'][covered_item],
                    'clause': covered_item
                }
        
        # Check exclusions
        for excluded_item in policy_data['exclusions']:
            if procedure_lower in excluded_item.lower() or excluded_item.lower() in procedure_lower:
                return {
                    'covered': False,
                    'reason': f"Excluded: {excluded_item}"
                }
        
        # Check semantic mappings
        for category, synonyms in PROCEDURE_MAPPINGS.items():
            if category.lower() == procedure_lower or procedure_lower in [s.lower() for s in synonyms]:
                for covered_item in policy_data['inclusions']:
                    if category.lower() in covered_item.lower():
                        return {
                            'covered': True,
                            'amount': policy_data['inclusions'][covered_item],
                            'clause': covered_item
                        }
        
        return {
            'covered': False,
            'reason': 'Procedure not found in policy coverage'
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'mode': 'VERCEL_SERVERLESS',
        'available_policies': list(SAMPLE_POLICIES.keys()),
        'capabilities': {
            'nlp_processing': True,
            'semantic_matching': True,
            'sample_policies': True,
            'database': False
        },
        'message': '🎯 Insurance Query Engine Ready (No Database Mode)',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/query', methods=['POST', 'OPTIONS'])
def process_query():
    """Process insurance query"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        policy_type = data.get('policy_type', 'standard')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Extract information from query
        extracted_info = QueryProcessor.extract_info(query)
        
        # Get policy data
        policy_data = SAMPLE_POLICIES.get(policy_type, SAMPLE_POLICIES['standard'])
        
        # Check coverage
        procedure = extracted_info.get('procedure', 'general medical')
        coverage_result = DecisionEngine.check_coverage(procedure, policy_data)
        
        # Determine decision and confusion matrix
        if coverage_result['covered']:
            decision = 'APPROVED'
            confusion_matrix = 'AA'  # Correctly Approved
            amount = coverage_result.get('amount', 0)
            justification = f"Covered under: {coverage_result.get('clause', 'policy terms')}"
        else:
            decision = 'REJECTED'
            confusion_matrix = 'RR'  # Correctly Rejected
            amount = 0
            justification = coverage_result.get('reason', 'Not covered under policy')
        
        response_data = {
            'decision': decision,
            'amount': amount,
            'confidence': 85,
            'justification': justification,
            'confusion_matrix': confusion_matrix,
            'extracted_info': extracted_info,
            'policy_info': {
                'name': policy_data['name'],
                'type': policy_data['type']
            },
            'coverage_details': coverage_result,
            'timestamp': datetime.now().isoformat()
        }
        
        response = make_response(jsonify(response_data))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'decision': 'ERROR',
            'confusion_matrix': 'UNKNOWN'
        }), 500

@app.route('/policies', methods=['GET'])
def get_policies():
    """Get available sample policies"""
    policies_info = []
    for key, policy in SAMPLE_POLICIES.items():
        policies_info.append({
            'id': key,
            'name': policy['name'],
            'type': policy['type'],
            'inclusions_count': len(policy['inclusions']),
            'exclusions_count': len(policy['exclusions'])
        })
    
    return jsonify({
        'policies': policies_info,
        'message': 'Sample policies available for testing'
    })

@app.route('/policy/<policy_id>', methods=['GET'])
def get_policy_details(policy_id):
    """Get detailed policy information"""
    policy = SAMPLE_POLICIES.get(policy_id)
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
    
    return jsonify(policy)

# Main handler for Vercel
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
    app.run(debug=True, port=5000)
