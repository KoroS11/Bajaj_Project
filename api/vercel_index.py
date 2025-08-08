#!/usr/bin/env python3
"""
🎯 VERCEL INSURANCE QUERY ENGINE WITH PDF UPLOAD
✅ Supports PDF uploads using Vercel Blob Storage
✅ Processes PDFs in real-time
✅ Works without traditional database
"""

import json
import os
import re
import base64
import tempfile
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# PDF processing capabilities
try:
    import pdfplumber
    import PyPDF2
    PDF_PROCESSING = True
except ImportError:
    PDF_PROCESSING = False

# Fuzzy matching
try:
    from rapidfuzz import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    try:
        from fuzzywuzzy import fuzz, process
        FUZZY_AVAILABLE = True
    except ImportError:
        FUZZY_AVAILABLE = False

# Store processed documents in memory (for current session)
session_documents = {}

# Procedure mappings
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

class DocumentProcessor:
    """Process PDF documents"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_content):
        """Extract text from PDF bytes"""
        if not PDF_PROCESSING:
            return "PDF processing libraries not available"
        
        text_content = ""
        
        # Save PDF content to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_content)
            tmp_path = tmp_file.name
        
        try:
            # Try pdfplumber first
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            if not text_content.strip():
                # Fallback to PyPDF2
                with open(tmp_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text_content += page.extract_text() + "\n"
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
        
        return text_content or "Unable to extract text from PDF"
    
    @staticmethod
    def extract_policy_clauses(text_content):
        """Extract policy information from text"""
        clauses = {
            'inclusions': {},
            'exclusions': [],
            'waiting_periods': {},
            'policy_info': {}
        }
        
        text_lower = text_content.lower()
        
        # Extract exclusions
        exclusion_patterns = [
            r'(?:exclusions?|not covered|excluded)[:\-\s]*(.+?)(?:\n\n|\d+\.|\bsection\b|$)',
            r'(?:this policy does not cover)[:\-\s]*(.+?)(?:\n\n|\d+\.|$)'
        ]
        
        for pattern in exclusion_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            for match in matches:
                exclusion_text = match.group(1).strip()
                exclusion_items = re.split(r'[;\n•\-\*]|\d+\.', exclusion_text)
                for item in exclusion_items:
                    item = item.strip().rstrip('.,')
                    if 5 < len(item) < 200:
                        clauses['exclusions'].append(item)
        
        # Extract inclusions/coverage
        coverage_patterns = [
            r'([a-zA-Z][^:\n]{3,50})[:\-]\s*(?:covered|coverage|benefit|included)(?:\s*up\s*to)?\s*₹?\s*(\d+(?:,\d{3})*)',
            r'([a-zA-Z][^:\n]{3,50})\s+(?:covered|included)\s*₹?\s*(\d+(?:,\d{3})*)'
        ]
        
        for pattern in coverage_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                try:
                    service = match.group(1).strip().lower()
                    amount_str = re.sub(r'[,₹\s]', '', match.group(2))
                    amount = int(amount_str) if amount_str.isdigit() else 0
                    
                    if len(service) > 3 and amount > 0:
                        clauses['inclusions'][service] = amount
                except:
                    continue
        
        # Detect policy type
        if any(term in text_lower for term in ['fertility', 'ivf', 'reproductive']):
            policy_type = "Fertility Policy"
        elif any(term in text_lower for term in ['premium', 'comprehensive', 'deluxe']):
            policy_type = "Premium Policy"
        else:
            policy_type = "Standard Policy"
        
        clauses['policy_info']['type'] = policy_type
        
        return clauses

class QueryProcessor:
    """Process natural language queries"""
    
    @staticmethod
    def extract_info(query):
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
        if any(term in query_lower for term in ['female', 'woman', 'f,', 'pregnant']):
            extracted['gender'] = 'female'
        elif any(term in query_lower for term in ['male', 'man', 'm,']):
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
        
        return extracted

class FuzzyMatcher:
    """Fuzzy matching for procedures"""
    
    @staticmethod
    def find_best_match(user_procedure, document_clauses, threshold=60):
        """Find best matching clauses"""
        if not FUZZY_AVAILABLE:
            return FuzzyMatcher._simple_match(user_procedure, document_clauses)
        
        matches = []
        
        # Check inclusions
        for service, amount in document_clauses.get('inclusions', {}).items():
            similarity = fuzz.partial_ratio(user_procedure.lower(), service.lower())
            if similarity >= threshold:
                matches.append({
                    'clause': service,
                    'confidence': similarity,
                    'type': 'inclusion',
                    'amount': amount
                })
        
        # Check exclusions
        for exclusion in document_clauses.get('exclusions', []):
            similarity = fuzz.partial_ratio(user_procedure.lower(), exclusion.lower())
            if similarity >= threshold:
                matches.append({
                    'clause': exclusion,
                    'confidence': similarity,
                    'type': 'exclusion',
                    'amount': 0
                })
        
        return sorted(matches, key=lambda x: x['confidence'], reverse=True)
    
    @staticmethod
    def _simple_match(user_procedure, document_clauses):
        """Simple matching without fuzzy library"""
        matches = []
        user_lower = user_procedure.lower()
        
        for service, amount in document_clauses.get('inclusions', {}).items():
            if user_lower in service.lower() or service.lower() in user_lower:
                matches.append({
                    'clause': service,
                    'confidence': 75,
                    'type': 'inclusion',
                    'amount': amount
                })
        
        for exclusion in document_clauses.get('exclusions', []):
            if user_lower in exclusion.lower() or exclusion.lower() in user_lower:
                matches.append({
                    'clause': exclusion,
                    'confidence': 75,
                    'type': 'exclusion',
                    'amount': 0
                })
        
        return matches

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """Handle PDF upload and processing"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read PDF content
        pdf_content = file.read()
        
        # Process PDF
        if PDF_PROCESSING:
            text_content = DocumentProcessor.extract_text_from_pdf(pdf_content)
            clauses = DocumentProcessor.extract_policy_clauses(text_content)
            
            # Generate session ID
            session_id = f"doc_{datetime.now().timestamp()}"
            
            # Store in session memory
            session_documents[session_id] = {
                'filename': file.filename,
                'text_content': text_content[:5000],  # Store first 5000 chars
                'clauses': clauses,
                'upload_time': datetime.now().isoformat()
            }
            
            # Store in Vercel Blob if available (optional)
            blob_url = None
            if os.environ.get('BLOB_READ_WRITE_TOKEN'):
                try:
                    # This would upload to Vercel Blob Storage
                    # You need to set up BLOB_READ_WRITE_TOKEN in Vercel environment
                    headers = {
                        'authorization': f"Bearer {os.environ.get('BLOB_READ_WRITE_TOKEN')}"
                    }
                    response = requests.put(
                        f"https://blob.vercel-storage.com/{file.filename}",
                        data=pdf_content,
                        headers=headers
                    )
                    if response.status_code == 200:
                        blob_url = response.json().get('url')
                except:
                    pass
            
            return jsonify({
                'status': 'success',
                'session_id': session_id,
                'filename': file.filename,
                'message': 'PDF processed successfully',
                'processing_result': {
                    'inclusions_found': len(clauses['inclusions']),
                    'exclusions_found': len(clauses['exclusions']),
                    'policy_type': clauses['policy_info'].get('type'),
                    'text_length': len(text_content)
                },
                'blob_url': blob_url
            })
        else:
            return jsonify({
                'error': 'PDF processing not available',
                'message': 'Please install pdfplumber and PyPDF2'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/query', methods=['POST', 'OPTIONS'])
def process_query():
    """Process insurance query with uploaded document"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        session_id = data.get('session_id', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Extract user information
        extracted_info = QueryProcessor.extract_info(query)
        
        # Get document from session or use default
        document_clauses = None
        if session_id and session_id in session_documents:
            document_clauses = session_documents[session_id]['clauses']
        
        if not document_clauses:
            # Use default policy if no document uploaded
            document_clauses = {
                'inclusions': {
                    'cardiac surgery': 500000,
                    'general medical': 100000,
                    'emergency treatment': 50000
                },
                'exclusions': ['ivf treatment', 'cosmetic surgery'],
                'policy_info': {'type': 'Standard Policy'}
            }
        
        # Find matches
        user_procedure = extracted_info.get('procedure', 'general medical')
        matches = FuzzyMatcher.find_best_match(user_procedure, document_clauses)
        
        # Make decision
        if matches and matches[0]['type'] == 'inclusion':
            decision = 'APPROVED'
            amount = matches[0]['amount']
            justification = f"Covered under: {matches[0]['clause']}"
            confusion_matrix = 'AA'
        elif matches and matches[0]['type'] == 'exclusion':
            decision = 'REJECTED'
            amount = 0
            justification = f"Excluded: {matches[0]['clause']}"
            confusion_matrix = 'RR'
        else:
            decision = 'REJECTED'
            amount = 0
            justification = 'No matching coverage found'
            confusion_matrix = 'RR'
        
        return jsonify({
            'decision': decision,
            'amount': amount,
            'confidence': matches[0]['confidence'] if matches else 50,
            'justification': justification,
            'confusion_matrix': confusion_matrix,
            'extracted_info': extracted_info,
            'policy_type': document_clauses['policy_info'].get('type'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'mode': 'VERCEL_WITH_PDF_UPLOAD',
        'capabilities': {
            'pdf_processing': PDF_PROCESSING,
            'fuzzy_matching': FUZZY_AVAILABLE,
            'session_documents': len(session_documents),
            'blob_storage': bool(os.environ.get('BLOB_READ_WRITE_TOKEN'))
        },
        'message': '🎯 Insurance Query Engine Ready with PDF Upload',
        'timestamp': datetime.now().isoformat()
    })

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
