import json

def handler(event, context):
    """
    Netlify Functions handler for the Bajaj Insurance API
    """
    
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    # Handle preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Main API logic
    try:
        # Simple health check endpoint
        if event.get('path') == '/.netlify/functions/api' or event.get('rawPath') == '/api':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': '🎯 Bajaj Insurance API is working!',
                    'status': 'success',
                    'features': [
                        'AI Decision Making',
                        'PDF Processing',
                        'Fuzzy Matching',
                        'Confusion Matrix Classification'
                    ]
                })
            }
        
        # Default response
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Welcome to Bajaj Insurance Query Engine API',
                'endpoints': {
                    'health': '/.netlify/functions/api',
                    'status': 'Active'
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'message': 'Internal server error'
            })
        }
import traceback
import uuid
import re
import os
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Ensure uploads directory exists
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Enhanced dependency checking
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✅ Gemini AI available")
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini AI not available")

# Advanced fuzzy matching with RapidFuzz
try:
    from rapidfuzz import fuzz, process
    FUZZY_AVAILABLE = True
    print("✅ RapidFuzz available - Advanced fuzzy matching enabled!")
except ImportError:
    try:
        from fuzzywuzzy import fuzz, process
        FUZZY_AVAILABLE = True
        print("✅ FuzzyWuzzy available - Basic fuzzy matching enabled!")
    except ImportError:
        FUZZY_AVAILABLE = False
        print("❌ No fuzzy matching library - Install with: pip install rapidfuzz")

# PDF processing capabilities
try:
    import pdfplumber
    import PyPDF2
    PDF_PROCESSING = True
    print("✅ PDF processing available")
except ImportError:
    PDF_PROCESSING = False
    print("❌ PDF processing not available")

# Document storage for dynamic processing
uploaded_documents = {}

# 🧠 SEMANTIC MAPPINGS FOR MEDICAL PROCEDURES
PROCEDURE_MAPPINGS = {
    'IVF': ['in vitro fertilization', 'fertility treatment', 'assisted reproduction', 'ivf', 'artificial insemination', 'fertility procedure'],
    'fertility': ['reproductive health', 'infertility treatment', 'conception assistance', 'fertility consultation', 'reproductive therapy'],
    'cardiac': ['heart surgery', 'cardiovascular', 'cardiac intervention', 'bypass surgery', 'angioplasty', 'heart operation'],
    'maternity': ['pregnancy care', 'prenatal', 'childbirth', 'delivery', 'maternity benefits', 'pregnancy benefits', 'prenatal care'],
    'cancer': ['oncology', 'chemotherapy', 'radiation therapy', 'tumor treatment', 'cancer therapy', 'malignancy treatment'],
    'emergency': ['urgent care', 'emergency room', 'trauma care', 'critical care', 'ambulance', 'emergency treatment'],
    'surgery': ['operation', 'surgical procedure', 'operative treatment', 'surgical intervention'],
    'diagnostic': ['tests', 'scans', 'diagnostics', 'medical tests', 'laboratory tests', 'imaging'],
    'consultation': ['doctor visit', 'medical consultation', 'physician visit', 'specialist consultation']
}

# 📊 POLICY TYPE CLASSIFICATIONS
POLICY_CLASSIFICATIONS = {
    'Standard Policy': {
        'covered': ['cardiac', 'general medical', 'emergency', 'surgery', 'diagnostic', 'consultation'],
        'excluded': ['IVF', 'fertility', 'cosmetic', 'experimental'],
        'waiting_periods': {'surgery': '24 months', 'cardiac': '48 months'}
    },
    'Fertility Policy': {
        'covered': ['IVF', 'fertility', 'maternity', 'general medical', 'diagnostic', 'consultation'],
        'excluded': ['cosmetic', 'experimental'],
        'waiting_periods': {'IVF': '12 months', 'fertility': '12 months'}
    },
    'Premium Policy': {
        'covered': ['cardiac', 'cancer', 'surgery', 'maternity', 'IVF', 'fertility', 'emergency', 'diagnostic'],
        'excluded': ['cosmetic', 'experimental'],
        'waiting_periods': {'surgery': '12 months', 'cardiac': '24 months'}
    }
}

class DocumentProcessor:
    """Complete Document Processing Module"""
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF using multiple methods for robustness"""
        text_content = ""
        
        if not PDF_PROCESSING:
            return "PDF processing not available. Install pdfplumber and PyPDF2."
        
        # Method 1: Try pdfplumber (better for formatted text)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            if text_content.strip():
                print(f"✅ PDF extracted using pdfplumber ({len(text_content)} chars)")
                return text_content
        except Exception as e:
            print(f"⚠️ pdfplumber failed: {e}")
        
        # Method 2: Fallback to PyPDF2
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
            if text_content.strip():
                print(f"✅ PDF extracted using PyPDF2 ({len(text_content)} chars)")
                return text_content
        except Exception as e:
            print(f"❌ PyPDF2 failed: {e}")
        
        return "Unable to extract text from PDF"
    
    @staticmethod
    def extract_policy_clauses(text_content):
        """Dynamically parse inclusion and exclusion clauses from document text"""
        print("🔍 Parsing insurance clauses from document...")
        
        clauses = {
            'inclusions': {},
            'exclusions': [],
            'waiting_periods': {},
            'coverage_amounts': {},
            'policy_info': {}
        }
        
        text_lower = text_content.lower()
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        # Enhanced exclusion parsing
        exclusion_patterns = [
            r'(?:exclusions?|not covered|excluded|exceptions?)[:\-\s]*(.+?)(?:\n\n|\d+\.|\bsection\b|\bcoverage\b|$)',
            r'(?:the following (?:are|is) (?:not )?(?:covered|excluded))[:\-\s]*(.+?)(?:\n\n|\d+\.|\bsection\b|$)',
            r'(?:this policy does not cover)[:\-\s]*(.+?)(?:\n\n|\d+\.|\bsection\b|$)',
            r'(?:not payable|will not pay|does not include)[:\-\s]*(.+?)(?:\n\n|\d+\.|\bsection\b|$)'
        ]
        
        for pattern in exclusion_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            for match in matches:
                exclusion_text = match.group(1).strip()
                exclusion_items = re.split(r'[;\n•\-\*]|(?:\d+\.)', exclusion_text)
                for item in exclusion_items:
                    item = item.strip().rstrip('.,')
                    if len(item) > 5 and len(item) < 200:
                        clauses['exclusions'].append(item)
        
        # Enhanced inclusion/coverage parsing with multiple patterns
        coverage_patterns = [
            r'([a-zA-Z][^:\n]{3,50})[:\-]\s*(?:covered|coverage|benefit|included)\s*(?:up\s*to)?\s*₹?\s*(\d+(?:,\d{3})*)',
            r'([a-zA-Z][^:\n]{3,50})\s+(?:covered|included)\s*₹?\s*(\d+(?:,\d{3})*)',
            r'₹?\s*(\d+(?:,\d{3})*)\s+(?:for|towards)\s+([a-zA-Z][^\n]{3,50})',
            r'([a-zA-Z][^:\-\n]{3,50})\s*[\-–]\s*₹?\s*(\d+(?:,\d{3})*)',
            r'([a-zA-Z][^:\n]{3,50})[:\-]\s*(?:covered|yes|included|available|payable)'
        ]
        
        for i, pattern in enumerate(coverage_patterns):
            matches = re.finditer(pattern, text_content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    if i < 4:  # First 4 patterns have amount
                        if i == 2:  # Pattern 3: amount comes first
                            service = match.group(2).strip().lower()
                            amount_str = match.group(1)
                        else:
                            service = match.group(1).strip().lower()
                            amount_str = match.group(2) if len(match.groups()) > 1 else "0"
                        
                        amount_str = re.sub(r'[,₹\s]', '', amount_str)
                        amount = int(amount_str) if amount_str.isdigit() else 0
                    else:  # Pattern 5: no amount, just coverage
                        service = match.group(1).strip().lower()
                        amount = 1  # Indicates coverage without specific amount
                    
                    service = re.sub(r'^\W+|\W+$', '', service)
                    service = re.sub(r'\s+', ' ', service)
                    
                    if len(service) > 3 and service not in ['the', 'and', 'for', 'with']:
                        clauses['inclusions'][service] = amount
                        if amount > 1:
                            clauses['coverage_amounts'][service] = f"₹{amount:,}"
                        else:
                            clauses['coverage_amounts'][service] = "Covered"
                        
                except (ValueError, IndexError, AttributeError):
                    continue
        
        # Policy type detection
        policy_type = "Standard Policy"  # Default
        if any(term in text_lower for term in ['fertility', 'ivf', 'reproductive']):
            policy_type = "Fertility Policy"
        elif any(term in text_lower for term in ['premium', 'comprehensive', 'deluxe']):
            policy_type = "Premium Policy"
        
        clauses['policy_info']['type'] = policy_type
        clauses['policy_info']['name'] = f"Policy Document ({policy_type})"
        
        # Clean up exclusions
        cleaned_exclusions = []
        for exclusion in clauses['exclusions']:
            exclusion = exclusion.strip().rstrip('.,;')
            if len(exclusion) > 5 and exclusion not in cleaned_exclusions:
                exclusion = re.sub(r'^(?:and|or|the|a|an)\s+', '', exclusion, flags=re.IGNORECASE)
                if exclusion and exclusion not in cleaned_exclusions:
                    cleaned_exclusions.append(exclusion)
        
        clauses['exclusions'] = cleaned_exclusions[:50]
        
        print(f"📋 Parsed {len(clauses['inclusions'])} inclusions, {len(clauses['exclusions'])} exclusions")
        print(f"🏷️ Policy type detected: {policy_type}")
        
        return clauses
    
    @staticmethod
    def identify_policy_type(text_content):
        """Identify policy type from document content"""
        text_lower = text_content.lower()
        
        # Score each policy type based on keyword presence
        scores = {'Standard Policy': 0, 'Fertility Policy': 0, 'Premium Policy': 0}
        
        # Fertility policy indicators
        fertility_keywords = ['fertility', 'ivf', 'in vitro', 'reproductive', 'infertility', 'conception']
        scores['Fertility Policy'] += sum(1 for keyword in fertility_keywords if keyword in text_lower)
        
        # Premium policy indicators
        premium_keywords = ['premium', 'comprehensive', 'deluxe', 'platinum', 'enhanced']
        scores['Premium Policy'] += sum(1 for keyword in premium_keywords if keyword in text_lower)
        
        # Standard policy (default with slight preference)
        scores['Standard Policy'] += 1
        
        return max(scores, key=scores.get)

class QueryProcessor:
    """Advanced Natural Language Query Processing Engine"""
    
    @staticmethod
    def extract_user_info(query):
        """Extract structured information from natural language query"""
        query_lower = query.lower()
        extracted = {}
        
        print(f"🔍 Extracting user information from: '{query}'")
        
        # Age extraction with multiple patterns
        age_patterns = [
            r'(\d+)\s*(?:year|yr)s?\s*old',
            r'(\d+)(?:y|Y|F|M)\b',
            r'age\s*[:\-]?\s*(\d+)',
            r'\b(\d+)\s*(?:year|yr)s?(?:\s+old)?'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, query)
            if match:
                age = int(match.group(1))
                if 0 < age < 120:  # Reasonable age range
                    extracted['age'] = age
                    break
        
        # Gender extraction
        gender_patterns = [
            r'\b(?:\d+)?([mf])\b',  # "25F", "45M", "F", "M"
            r'\b(male|female|man|woman)\b',
            r'\b(pregnant)\b'  # Implies female
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, query_lower)
            if match:
                gender_text = match.group(1).lower()
                if gender_text in ['f', 'female', 'woman', 'pregnant']:
                    extracted['gender'] = 'female'
                elif gender_text in ['m', 'male', 'man']:
                    extracted['gender'] = 'male'
                break
        
        # Procedure extraction using semantic mapping
        best_procedure = None
        best_score = 0
        
        for category, synonyms in PROCEDURE_MAPPINGS.items():
            for synonym in synonyms:
                if synonym.lower() in query_lower:
                    score = len(synonym) * 2  # Longer matches get higher scores
                    if score > best_score:
                        best_score = score
                        best_procedure = category
        
        if best_procedure:
            extracted['procedure'] = best_procedure
            extracted['procedure_confidence'] = min(95, best_score)
        else:
            # Fallback: extract any medical-sounding terms
            medical_terms = re.findall(r'\b(?:treatment|surgery|procedure|therapy|care|consultation|test|scan|operation|visit)\b', query_lower)
            if medical_terms:
                extracted['procedure'] = f"medical {medical_terms[0]}"
                extracted['procedure_confidence'] = 60
        
        # Policy duration extraction
        duration_patterns = [
            r'(?:policy|coverage).*?(\d+)\s*(?:year|yr|month)s?',
            r'active.*?(?:since|for).*?(\d+)\s*(?:year|yr|month)s?',
            r'(\d+)\s*(?:year|yr|month)s?.*?(?:policy|coverage)'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, query_lower)
            if match:
                duration = int(match.group(1))
                unit = 'years' if 'year' in match.group(0) or 'yr' in match.group(0) else 'months'
                extracted['policy_duration'] = f"{duration} {unit}"
                break
        
        # Medical history indicators
        history_keywords = ['history', 'previous', 'past', 'chronic', 'existing']
        if any(keyword in query_lower for keyword in history_keywords):
            extracted['has_medical_history'] = True
        
        print(f"📊 Extracted info: {extracted}")
        return extracted

class FuzzyMatcher:
    """Advanced Fuzzy Logic Engine with Semantic Understanding"""
    
    @staticmethod
    def find_best_match(user_procedure, document_clauses, threshold=70):
        """Find best matching clauses with confidence scores"""
        if not FUZZY_AVAILABLE:
            return FuzzyMatcher._fallback_matching(user_procedure, document_clauses, threshold)
        
        matches = []
        
        # Check inclusions
        for service, amount in document_clauses.get('inclusions', {}).items():
            similarity = fuzz.partial_ratio(user_procedure.lower(), service.lower())
            if similarity >= threshold:
                matches.append({
                    'clause': service,
                    'confidence': similarity,
                    'type': 'inclusion',
                    'amount': amount,
                    'section': 'inclusions'
                })
        
        # Check exclusions
        for exclusion in document_clauses.get('exclusions', []):
            similarity = fuzz.partial_ratio(user_procedure.lower(), exclusion.lower())
            if similarity >= threshold:
                matches.append({
                    'clause': exclusion,
                    'confidence': similarity,
                    'type': 'exclusion',
                    'amount': 0,
                    'section': 'exclusions'
                })
        
        # Semantic matching using procedure mappings
        if user_procedure in PROCEDURE_MAPPINGS:
            synonyms = PROCEDURE_MAPPINGS[user_procedure]
            for synonym in synonyms:
                for service in document_clauses.get('inclusions', {}):
                    similarity = fuzz.partial_ratio(synonym.lower(), service.lower())
                    if similarity >= threshold - 10:  # Slightly lower threshold for semantic matches
                        matches.append({
                            'clause': service,
                            'confidence': similarity + 5,  # Bonus for semantic match
                            'type': 'inclusion',
                            'amount': document_clauses['inclusions'][service],
                            'section': 'inclusions_semantic'
                        })
        
        return sorted(matches, key=lambda x: x['confidence'], reverse=True)
    
    @staticmethod
    def _fallback_matching(user_procedure, document_clauses, threshold):
        """Fallback matching without fuzzy libraries"""
        matches = []
        user_lower = user_procedure.lower()
        
        # Simple substring matching
        for service, amount in document_clauses.get('inclusions', {}).items():
            if user_lower in service.lower() or service.lower() in user_lower:
                confidence = 80 if user_lower == service.lower() else 70
                matches.append({
                    'clause': service,
                    'confidence': confidence,
                    'type': 'inclusion',
                    'amount': amount,
                    'section': 'inclusions'
                })
        
        for exclusion in document_clauses.get('exclusions', []):
            if user_lower in exclusion.lower() or exclusion.lower() in user_lower:
                confidence = 80 if user_lower == exclusion.lower() else 70
                matches.append({
                    'clause': exclusion,
                    'confidence': confidence,
                    'type': 'exclusion',
                    'amount': 0,
                    'section': 'exclusions'
                })
        
        return sorted(matches, key=lambda x: x['confidence'], reverse=True)

class DecisionEngine:
    """Intelligent Decision Engine with Confusion Matrix Classification"""
    
    @staticmethod
    def make_decision(matches, extracted_info, document_clauses):
        """Make intelligent coverage decision with confusion matrix classification"""
        
        # Determine actual coverage (ground truth)
        policy_type = document_clauses.get('policy_info', {}).get('type', 'Standard Policy')
        user_procedure = extracted_info.get('procedure', 'unknown')
        
        actual_coverage = DecisionEngine._check_actual_coverage(user_procedure, policy_type, extracted_info)
        
        # Make system decision
        system_decision = DecisionEngine._make_system_decision(matches, extracted_info, document_clauses)
        
        # Classify using confusion matrix
        confusion_class = DecisionEngine._classify_confusion_matrix(actual_coverage, system_decision['decision'])
        
        # Build comprehensive response
        response = {
            'decision': system_decision['decision'],
            'amount': system_decision['amount'],
            'confidence': system_decision['confidence'],
            'justification': system_decision['justification'],
            'confusion_matrix': confusion_class,
            'actual_coverage': actual_coverage,
            'system_reasoning': system_decision['reasoning'],
            'best_match_clause': system_decision.get('best_clause'),
            'similarity_score': system_decision.get('similarity_score', 0),
            'policy_type': policy_type,
            'waiting_period_check': DecisionEngine._check_waiting_period(user_procedure, extracted_info, policy_type)
        }
        
        return response
    
    @staticmethod
    def _check_actual_coverage(procedure, policy_type, extracted_info):
        """Determine ground truth coverage based on policy rules"""
        policy_rules = POLICY_CLASSIFICATIONS.get(policy_type, POLICY_CLASSIFICATIONS['Standard Policy'])
        
        # Check if procedure type is covered
        procedure_type = procedure.lower()
        
        # Direct match in covered procedures
        if any(covered in procedure_type for covered in policy_rules['covered']):
            return True
        
        # Direct match in excluded procedures  
        if any(excluded in procedure_type for excluded in policy_rules['excluded']):
            return False
        
        # Semantic matching
        for covered_type in policy_rules['covered']:
            if covered_type in PROCEDURE_MAPPINGS:
                synonyms = PROCEDURE_MAPPINGS[covered_type]
                if any(synonym.lower() in procedure_type for synonym in synonyms):
                    return True
        
        # Default based on policy type
        return policy_type != 'Standard Policy'  # More permissive for non-standard policies
    
    @staticmethod
    def _make_system_decision(matches, extracted_info, document_clauses):
        """Make system decision based on document analysis"""
        
        if not matches:
            return {
                'decision': 'REJECTED',
                'amount': 0,
                'confidence': 50,
                'justification': 'No matching coverage found in policy document',
                'reasoning': 'fallback_no_matches'
            }
        
        best_match = matches[0]
        
        if best_match['type'] == 'exclusion':
            return {
                'decision': 'REJECTED',
                'amount': 0,
                'confidence': best_match['confidence'],
                'justification': f"Procedure excluded under policy clause: '{best_match['clause']}'",
                'reasoning': 'explicit_exclusion',
                'best_clause': best_match['clause'],
                'similarity_score': best_match['confidence']
            }
        
        elif best_match['type'] == 'inclusion':
            amount = best_match.get('amount', 0)
            return {
                'decision': 'APPROVED',
                'amount': amount if amount > 1 else 0,
                'confidence': best_match['confidence'],
                'justification': f"Procedure covered under policy clause: '{best_match['clause']}'" + (f" with coverage amount ₹{amount:,}" if amount > 1 else ""),
                'reasoning': 'explicit_inclusion',
                'best_clause': best_match['clause'],
                'similarity_score': best_match['confidence']
            }
        
        else:
            return {
                'decision': 'REJECTED',
                'amount': 0,
                'confidence': 60,
                'justification': 'Unable to determine coverage from available policy information',
                'reasoning': 'insufficient_information'
            }
    
    @staticmethod
    def _classify_confusion_matrix(actual_coverage, system_decision):
        """Classify result using confusion matrix (RR, RA, AR, AA)"""
        
        actual_positive = actual_coverage  # True if should be covered
        predicted_positive = (system_decision == 'APPROVED')  # True if system approves
        
        if not actual_positive and not predicted_positive:
            return 'RR'  # True Negative: Correctly Rejected
        elif actual_positive and predicted_positive:
            return 'AA'  # True Positive: Correctly Approved
        elif not actual_positive and predicted_positive:
            return 'RA'  # False Positive: Incorrectly Approved
        elif actual_positive and not predicted_positive:
            return 'AR'  # False Negative: Incorrectly Rejected
        else:
            return 'UNKNOWN'
    
    @staticmethod
    def _check_waiting_period(procedure, extracted_info, policy_type):
        """Check if waiting period requirements are met"""
        policy_rules = POLICY_CLASSIFICATIONS.get(policy_type, {})
        waiting_periods = policy_rules.get('waiting_periods', {})
        
        policy_duration = extracted_info.get('policy_duration', '')
        
        # Extract duration in months
        duration_months = 0
        if 'month' in policy_duration:
            duration_months = int(re.search(r'(\d+)', policy_duration).group(1))
        elif 'year' in policy_duration:
            years = int(re.search(r'(\d+)', policy_duration).group(1))
            duration_months = years * 12
        
        # Check waiting period for procedure type
        procedure_type = procedure.lower()
        for wait_type, wait_period in waiting_periods.items():
            if wait_type.lower() in procedure_type:
                required_months = int(re.search(r'(\d+)', wait_period).group(1))
                if 'year' in wait_period:
                    required_months *= 12
                
                return {
                    'required_waiting_period': wait_period,
                    'policy_duration_months': duration_months,
                    'waiting_period_met': duration_months >= required_months,
                    'waiting_period_applicable': True
                }
        
        return {'waiting_period_applicable': False}

def load_existing_documents():
    """Load existing documents from uploads folder on server startup"""
    print("🔄 Loading existing documents from uploads folder...")
    
    if not os.path.exists(UPLOAD_FOLDER):
        print("📂 No uploads folder found")
        return
    
    files = os.listdir(UPLOAD_FOLDER)
    pdf_files = [f for f in files if f.endswith('.pdf')]
    
    print(f"📄 Found {len(pdf_files)} PDF files in uploads folder")
    
    for filename in pdf_files[:5]:  # Load first 5 to avoid startup delays
        try:
            file_id = str(uuid.uuid4())
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file_size = os.path.getsize(file_path)
            
            if PDF_PROCESSING:
                text_content = DocumentProcessor.extract_text_from_pdf(file_path)
                clauses = DocumentProcessor.extract_policy_clauses(text_content)
                
                uploaded_documents[file_id] = {
                    'filename': filename,
                    'file_path': file_path,
                    'text_content': text_content,
                    'clauses': clauses,
                    'upload_time': datetime.now().isoformat(),
                    'file_size': file_size
                }
                
                print(f"✅ Loaded: {filename} ({file_size} bytes)")
            else:
                print(f"⚠️ PDF processing disabled, skipping: {filename}")
                
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
    
    print(f"📋 Total documents loaded: {len(uploaded_documents)}")

# Load existing documents on startup
load_existing_documents()

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """Handle file upload with comprehensive processing"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
    
    try:
        print("📤 File upload request received")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided', 'status': 'failed'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected', 'status': 'failed'}), 400
        
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.txt'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'File type {file_ext} not supported. Allowed: {", ".join(allowed_extensions)}', 'status': 'failed'}), 400
        
        # Generate unique file ID and save file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{file.filename}")
        
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        print(f"✅ File saved: {file_path} ({file_size} bytes)")
        
        # Process document content
        processing_result = None
        if file_ext == '.pdf' and PDF_PROCESSING:
            try:
                print("🔍 Processing PDF content...")
                text_content = DocumentProcessor.extract_text_from_pdf(file_path)
                clauses = DocumentProcessor.extract_policy_clauses(text_content)
                policy_type = DocumentProcessor.identify_policy_type(text_content)
                
                # Store the processed document
                uploaded_documents[file_id] = {
                    'filename': file.filename,
                    'file_path': file_path,
                    'text_content': text_content,
                    'clauses': clauses,
                    'upload_time': datetime.now().isoformat(),
                    'file_size': file_size,
                    'policy_type': policy_type
                }
                
                processing_result = {
                    'inclusions_found': len(clauses['inclusions']),
                    'exclusions_found': len(clauses['exclusions']),
                    'policy_name': clauses['policy_info'].get('name', 'Unknown Policy'),
                    'policy_type': policy_type,
                    'waiting_periods': len(clauses['waiting_periods']),
                    'text_length': len(text_content)
                }
                
                print(f"✅ Document processed: {processing_result}")
                
            except Exception as e:
                print(f"⚠️ PDF processing failed: {e}")
                processing_result = {'error': f'PDF processing failed: {str(e)}'}
        
        response_data = {
            'file_id': file_id,
            'status': 'uploaded',
            'message': f'File "{file.filename}" uploaded and processed successfully',
            'filename': file.filename,
            'size': file_size,
            'size_display': f"{round(file_size/1024)} KB",
            'pdf_processing': PDF_PROCESSING,
            'fuzzy_matching': FUZZY_AVAILABLE,
            'processing_result': processing_result,
            'upload_timestamp': datetime.now().isoformat()
        }
        
        response = make_response(jsonify(response_data))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        traceback.print_exc()
        response_data = {
            'error': f'Upload failed: {str(e)}',
            'status': 'failed'
        }
        response = make_response(jsonify(response_data), 500)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

@app.route('/query', methods=['POST', 'OPTIONS'])
def process_query():
    """Process insurance query with complete intelligent analysis"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        file_id = data.get('file_id', '')
        request_id = str(uuid.uuid4())[:8]
        
        print(f"\n🎯 INTELLIGENT PROCESSING [ID: {request_id}]")
        print(f"📝 Query: '{query}'")
        print(f"📄 File ID: '{file_id}'")
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Extract user information using NLP
        extracted_info = QueryProcessor.extract_user_info(query)
        print(f"🔍 Extracted info: {extracted_info}")
        
        # Get document clauses
        document_clauses = None
        document_info = {}
        
        # Use uploaded document
        if uploaded_documents:
            if not file_id or file_id not in uploaded_documents:
                file_id = max(uploaded_documents.keys(), key=lambda x: uploaded_documents[x]['upload_time'])
                print(f"🔄 Using most recent upload: {file_id}")
            
            if file_id in uploaded_documents:
                doc_data = uploaded_documents[file_id]
                document_clauses = doc_data['clauses']
                document_info = {
                    'source': 'uploaded_document',
                    'filename': doc_data['filename'],
                    'policy_name': document_clauses['policy_info'].get('name', 'Unknown Policy'),
                    'policy_type': doc_data.get('policy_type', 'Standard Policy'),
                    'processed_at': doc_data['upload_time'],
                    'file_size': doc_data['file_size'],
                    'size_display': f"{round(doc_data['file_size']/1024)} KB"
                }
                print(f"📋 Using document: {doc_data['filename']}")
        
        if document_clauses is None:
            return jsonify({
                'error': 'No PDF documents uploaded. Please upload a policy document first.',
                'request_id': request_id,
                'instructions': {
                    'step1': 'Upload a PDF policy document using the upload interface',
                    'step2': 'Submit your query after successful document upload',
                    'note': 'System requires actual policy documents for intelligent analysis'
                }
            }), 400
        
        # Fuzzy matching analysis
        user_procedure = extracted_info.get('procedure', query)
        matches = FuzzyMatcher.find_best_match(user_procedure, document_clauses, threshold=60)
        
        print(f"🔍 Fuzzy matches found: {len(matches)}")
        if matches:
            print(f"   Best match: {matches[0]['clause']} ({matches[0]['confidence']}% confidence)")
        
        # Intelligent decision making
        decision_result = DecisionEngine.make_decision(matches, extracted_info, document_clauses)
        print(f"📊 Decision result: {decision_result}")
        
        # Build comprehensive response per specifications
        response_data = {
            'decision': decision_result['decision'],
            'amount': decision_result['amount'],
            'confidence': decision_result['confidence'],
            'justification': decision_result['justification'],
            'confusion_matrix': decision_result['confusion_matrix'],
            'document_info': {
                'policy_name': document_info.get('policy_name'),
                'file_size': document_info.get('size_display'),
                'upload_status': 'successful',
                'policy_type': document_info.get('policy_type'),
                'filename': document_info.get('filename'),
                'processed_at': document_info.get('processed_at')
            },
            'coverage_match': matches[0]['type'] if matches else 'fallback',
            'extracted_info': {
                'age': extracted_info.get('age'),
                'gender': extracted_info.get('gender'),
                'procedure': extracted_info.get('procedure'),
                'policy_duration': extracted_info.get('policy_duration')
            },
            'matching_details': {
                'best_match_clause': decision_result.get('best_match_clause'),
                'similarity_score': decision_result.get('similarity_score', 0),
                'alternative_matches': [{'clause': m['clause'], 'confidence': m['confidence']} for m in matches[1:3]]
            },
            'system_capabilities': {
                'dynamic_pdf_processing': PDF_PROCESSING,
                'advanced_fuzzy_matching': FUZZY_AVAILABLE,
                'gemini_ai': GEMINI_AVAILABLE,
                'confusion_matrix_support': True,
                'nlp_processing': True
            },
            'processing_details': {
                'inclusions_checked': len(document_clauses.get('inclusions', {})),
                'exclusions_checked': len(document_clauses.get('exclusions', [])),
                'matches_found': len(matches),
                'policy_type': document_info.get('policy_type'),
                'waiting_period_check': decision_result.get('waiting_period_check')
            },
            'request_id': request_id,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ INTELLIGENT RESPONSE: {response_data['decision']} - {response_data['confusion_matrix']} (Confidence: {response_data['confidence']}%)")
        
        response = make_response(jsonify(response_data))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
        
    except Exception as e:
        print(f"❌ Query processing error: {str(e)}")
        traceback.print_exc()
        response_data = {
            'decision': 'ERROR',
            'amount': 0,
            'confidence': 0,
            'justification': f'Processing failed: {str(e)}',
            'confusion_matrix': 'UNKNOWN',
            'error': str(e)
        }
        response = make_response(jsonify(response_data), 500)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

@app.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint"""
    document_list = []
    
    for file_id, doc_data in uploaded_documents.items():
        document_list.append({
            'file_id': file_id,
            'filename': doc_data['filename'],
            'policy_type': doc_data.get('policy_type', 'Unknown'),
            'inclusions': len(doc_data['clauses']['inclusions']),
            'exclusions': len(doc_data['clauses']['exclusions']),
            'upload_time': doc_data['upload_time'],
            'size': f"{round(doc_data['file_size']/1024)} KB"
        })
    
    return jsonify({
        'status': 'healthy',
        'server_mode': 'INTELLIGENT_PROCESSING',
        'uploaded_documents': len(uploaded_documents),
        'documents': document_list,
        'system_capabilities': {
            'gemini_ai': GEMINI_AVAILABLE,
            'fuzzy_matching': FUZZY_AVAILABLE,
            'pdf_processing': PDF_PROCESSING,
            'intelligent_nlp': True,
            'confusion_matrix_classification': True,
            'semantic_matching': True,
            'mock_data': False
        },
        'policy_types_supported': list(POLICY_CLASSIFICATIONS.keys()),
        'procedure_mappings': list(PROCEDURE_MAPPINGS.keys()),
        'timestamp': datetime.now().isoformat(),
        'message': f"🎯 Intelligent Insurance Query Engine Ready - {len(uploaded_documents)} document(s) loaded"
    })

if __name__ == '__main__':
    print("\n🚀 STARTING INTELLIGENT INSURANCE QUERY ENGINE")
    print("="*60)
    
    print("📋 System Capabilities:")
    print(f"  🔍 PDF Processing: {'✅ Enabled' if PDF_PROCESSING else '❌ Disabled'}")
    print(f"  🧠 Advanced Fuzzy Matching: {'✅ Enabled' if FUZZY_AVAILABLE else '❌ Disabled'}")
    print(f"  🤖 Gemini AI: {'✅ Enabled' if GEMINI_AVAILABLE else '❌ Disabled'}")
    print(f"  📊 Confusion Matrix Classification: ✅ Enabled")
    print(f"  🔤 Natural Language Processing: ✅ Enabled")
    print(f"  🎯 Semantic Matching: ✅ Enabled")
    
    print(f"\n📄 Document Status:")
    print(f"  📂 Documents Loaded: {len(uploaded_documents)}")
    print(f"  🏷️  Policy Types: {', '.join(POLICY_CLASSIFICATIONS.keys())}")
    print(f"  🔍 Procedure Mappings: {len(PROCEDURE_MAPPINGS)} categories")
    
    if uploaded_documents:
        print("  📋 Available Documents:")
        for file_id, doc_data in list(uploaded_documents.items())[:3]:
            policy_type = doc_data.get('policy_type', 'Unknown')
            size_kb = round(doc_data['file_size']/1024)
            print(f"    • {doc_data['filename']} ({policy_type}, {size_kb} KB)")
        if len(uploaded_documents) > 3:
            print(f"    ... and {len(uploaded_documents) - 3} more")
    
    print(f"\n🌐 Server Information:")
    print(f"  🔗 URL: http://localhost:5000")
    print(f"  📋 Health Check: http://localhost:5000/health")
    print(f"  🖥️  Frontend: Open frontend/working_interface.html")
    
    print("="*60)
    print("🎯 INTELLIGENT QUERY ENGINE READY")
    print("📊 Confusion Matrix Classifications: RR, RA, AR, AA")
    print("🧠 Advanced NLP and Semantic Matching Enabled")
    print("Press Ctrl+C to stop\n")
    
    try:
        import os
        port = int(os.environ.get("PORT", 5000))
        app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        traceback.print_exc()
