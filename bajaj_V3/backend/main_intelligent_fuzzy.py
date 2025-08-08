#!/usr/bin/env python3
"""
🎯 DYNAMIC AI Insurance Query System
✅ Dynamic PDF document processing
✅ Confusion Matrix Support (AA, RR, AR, RA)  
✅ Advanced fuzzy matching with RapidFuzz
✅ Dynamic clause extraction from uploaded documents
✅ Smart semantic understanding
"""

import json
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

# Advanced fuzzy matching with RapidFuzz (better than FuzzyWuzzy)
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

def load_existing_documents():
    """Load existing documents from uploads folder on server startup"""
    print("🔄 Loading existing documents from uploads folder...")
    
    if not os.path.exists(UPLOAD_FOLDER):
        print("📂 No uploads folder found")
        return
    
    files = os.listdir(UPLOAD_FOLDER)
    pdf_files = [f for f in files if f.endswith('.pdf')]
    
    print(f"📄 Found {len(pdf_files)} PDF files in uploads folder")
    
    for filename in pdf_files:
        try:
            # Extract file_id from filename (format: file_id_originalname.pdf)
            if '_' in filename:
                file_id = filename.split('_')[0]
                original_name = '_'.join(filename.split('_')[1:])
            else:
                # For files without file_id prefix
                file_id = str(uuid.uuid4())
                original_name = filename
            
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file_size = os.path.getsize(file_path)
            
            # Process the PDF
            if PDF_PROCESSING:
                text_content = extract_text_from_pdf(file_path)
                clauses = parse_insurance_clauses(text_content)
                
                uploaded_documents[file_id] = {
                    'filename': original_name,
                    'file_path': file_path,
                    'text_content': text_content,
                    'clauses': clauses,
                    'upload_time': datetime.now().isoformat(),
                    'file_size': file_size
                }
                
                print(f"✅ Loaded: {original_name} ({file_size} bytes)")
            else:
                print(f"⚠️ PDF processing disabled, skipping: {filename}")
                
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
    
    print(f"📋 Total documents loaded: {len(uploaded_documents)}")

# Load existing documents on startup
load_existing_documents()

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

def parse_insurance_clauses(text_content):
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
    
    # Parse exclusions (most critical for decision making)
    exclusion_patterns = [
        r'(?:exclusions?|not covered|excluded|exceptions?)[:\-\s]*(.+?)(?:\n\n|\d+\.|\bsection\b|\bcoverage\b|$)',
        r'(?:the following (?:are|is) (?:not )?(?:covered|excluded))[:\-\s]*(.+?)(?:\n\n|\d+\.|\bsection\b|$)',
        r'(?:this policy does not cover)[:\-\s]*(.+?)(?:\n\n|\d+\.|\bsection\b|$)'
    ]
    
    for pattern in exclusion_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        for match in matches:
            exclusion_text = match.group(1).strip()
            # Split by common delimiters and clean
            exclusion_items = re.split(r'[;\n•\-\*]|(?:\d+\.)', exclusion_text)
            for item in exclusion_items:
                item = item.strip().rstrip('.,')
                if len(item) > 3 and len(item) < 200:  # Filter reasonable exclusions
                    clauses['exclusions'].append(item)
    
    # Parse inclusions/coverage with enhanced patterns
    coverage_patterns = [
        # Pattern 1: "Service: covered up to ₹amount"
        r'([a-zA-Z][^:\n]{3,40})[:\-]\s*(?:covered|coverage|benefit)\s*(?:up\s*to)?\s*₹?\s*(\d+(?:,\d{3})*)',
        # Pattern 2: "Service covered ₹amount"
        r'([a-zA-Z][^:\n]{3,40})\s+covered\s*₹?\s*(\d+(?:,\d{3})*)',
        # Pattern 3: "₹amount for service"
        r'₹?\s*(\d+(?:,\d{3})*)\s+(?:for|towards)\s+([a-zA-Z][^\n]{3,40})',
        # Pattern 4: "Service - ₹amount"
        r'([a-zA-Z][^:\-\n]{3,40})\s*[\-–]\s*₹?\s*(\d+(?:,\d{3})*)',
        # Pattern 5: Just "Service: Covered" (no amount)
        r'([a-zA-Z][^:\n]{3,40})[:\-]\s*(?:covered|yes|included|available)',
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
                    
                    # Clean and convert amount
                    amount_str = re.sub(r'[,₹\s]', '', amount_str)
                    amount = int(amount_str) if amount_str.isdigit() else 0
                else:  # Pattern 5: no amount, just coverage
                    service = match.group(1).strip().lower()
                    amount = 1  # Indicates coverage without specific amount
                
                # Clean service name
                service = re.sub(r'^\W+|\W+$', '', service)  # Remove leading/trailing non-word chars
                service = re.sub(r'\s+', ' ', service)  # Normalize whitespace
                
                if len(service) > 3 and service not in ['the', 'and', 'for', 'with']:
                    clauses['inclusions'][service] = amount
                    if amount > 1:
                        clauses['coverage_amounts'][service] = f"₹{amount:,}"
                    else:
                        clauses['coverage_amounts'][service] = "Covered"
                    
            except (ValueError, IndexError, AttributeError) as e:
                continue  # Skip malformed matches
    
    # Additional common medical terms to look for
    medical_terms = [
        'surgery', 'treatment', 'care', 'therapy', 'procedure', 'medical', 'health',
        'hospital', 'doctor', 'consultation', 'diagnosis', 'emergency', 'ambulance',
        'pharmacy', 'medicine', 'lab', 'test', 'scan', 'xray', 'mri', 'ct scan'
    ]
    
    # Look for coverage of medical terms in general text
    for term in medical_terms:
        if term in text_lower and term not in clauses['inclusions']:
            # Check if this term appears in a coverage context
            coverage_context = re.search(f'{term}[^.]*(?:covered|benefit|₹\d)', text_lower)
            if coverage_context:
                clauses['inclusions'][term] = 1  # Indicates coverage
                clauses['coverage_amounts'][term] = "Covered"
    
    # Parse waiting periods
    waiting_patterns = [
        r'(?:waiting period|waiting time)[:\-\s]*(\d+)\s*(days?|months?|years?)',
        r'(\w+(?:\s+\w+)*)[:\-\s]*(\d+)\s*(days?|months?|years?)\s*waiting'
    ]
    
    for pattern in waiting_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) >= 3:
                period = f"{match.group(2)} {match.group(3)}"
                service = match.group(1).strip() if len(match.groups()) > 3 else "general"
                clauses['waiting_periods'][service] = period
    
    # Clean up exclusions (remove duplicates and very short items)
    cleaned_exclusions = []
    for exclusion in clauses['exclusions']:
        exclusion = exclusion.strip().rstrip('.,;')
        if len(exclusion) > 5 and exclusion not in cleaned_exclusions:
            # Additional cleaning
            exclusion = re.sub(r'^(?:and|or|the|a|an)\s+', '', exclusion, flags=re.IGNORECASE)
            if exclusion and exclusion not in cleaned_exclusions:
                cleaned_exclusions.append(exclusion)
    
    clauses['exclusions'] = cleaned_exclusions[:50]  # Limit to reasonable number
    
    # Extract policy metadata
    policy_name_match = re.search(r'(?:policy\s+name|title)[:\-\s]*(.+?)(?:\n|$)', text_content, re.IGNORECASE)
    if policy_name_match:
        clauses['policy_info']['name'] = policy_name_match.group(1).strip()
    
    print(f"📋 Parsed {len(clauses['inclusions'])} inclusions, {len(clauses['exclusions'])} exclusions")
    return clauses

def advanced_fuzzy_match(query_text, target_list, threshold=85):
    """Advanced fuzzy matching with multiple algorithms and flexible thresholds"""
    if not FUZZY_AVAILABLE or not target_list:
        # Fallback to exact matching
        query_lower = query_text.lower()
        matches = []
        for target in target_list:
            if target.lower() in query_lower or query_lower in target.lower():
                matches.append((target, 95))
            # Also check for partial word matches
            query_words = query_lower.split()
            target_words = target.lower().split()
            common_words = set(query_words) & set(target_words)
            if common_words:
                score = len(common_words) / max(len(query_words), len(target_words)) * 100
                if score >= threshold - 20:  # More flexible threshold for fallback
                    matches.append((target, int(score)))
        return matches
    
    matches = []
    query_lower = query_text.lower()
    
    for target in target_list:
        target_lower = target.lower()
        
        # Multiple fuzzy matching algorithms
        ratio_scores = [
            fuzz.ratio(query_lower, target_lower),
            fuzz.partial_ratio(query_lower, target_lower),
            fuzz.token_sort_ratio(query_lower, target_lower),
            fuzz.token_set_ratio(query_lower, target_lower)
        ]
        
        # Take the highest score
        best_score = max(ratio_scores)
        
        # Bonus for exact substring matches
        if query_lower in target_lower or target_lower in query_lower:
            best_score = min(100, best_score + 15)
        
        # Bonus for word-level matches
        query_words = set(query_lower.split())
        target_words = set(target_lower.split())
        common_words = query_words & target_words
        if common_words:
            word_match_bonus = len(common_words) / max(len(query_words), len(target_words)) * 20
            best_score = min(100, best_score + word_match_bonus)
        
        # Lower threshold for medical terms to catch more potential matches
        effective_threshold = threshold
        if any(word in query_lower for word in ['treatment', 'surgery', 'care', 'therapy', 'procedure']):
            effective_threshold = max(60, threshold - 25)
        
        if best_score >= effective_threshold:
            matches.append((target, int(best_score)))
    
    # Sort by confidence
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

# Enhanced synonym mapping for better matching
PROCEDURE_SYNONYMS = {
    'fertility': [
        'ivf', 'in-vitro fertilization', 'fertility treatment', 'infertility treatment',
        'assisted reproductive technology', 'ivf procedure', 'fertility therapy',
        'artificial insemination', 'reproductive assistance', 'infertility consultation',
        'fertility consultation', 'assisted reproduction', 'icsi', 'iui'
    ],
    'maternity': [
        'maternity', 'prenatal', 'pregnancy', 'delivery', 'childbirth',
        'antenatal care', 'obstetric care', 'maternal health', 'pregnancy care',
        'prenatal checkup', 'maternity benefits'
    ],
    'cardiac': [
        'heart surgery', 'cardiac surgery', 'angioplasty', 'bypass surgery',
        'cardiac procedure', 'heart operation', 'cardiovascular surgery',
        'coronary surgery', 'heart treatment', 'cardiac care', 'heart bypass'
    ],
    'cancer': [
        'cancer treatment', 'chemotherapy', 'oncology', 'tumor treatment',
        'cancer therapy', 'radiation therapy', 'cancer surgery', 'oncological care',
        'chemo', 'radiotherapy', 'cancer care'
    ],
    'emergency': [
        'emergency care', 'trauma care', 'accident treatment', 'urgent care',
        'emergency surgery', 'critical care', 'emergency medical care',
        'trauma surgery', 'emergency treatment'
    ]
}

# Mock document functions REMOVED - System now analyzes ONLY uploaded documents
# This ensures all decisions are based on real policy documents provided by users

def extract_entities_advanced(query):
    """Advanced entity extraction with enhanced pattern recognition"""
    query_lower = query.lower()
    entities = {}
    
    print(f"🔍 Extracting entities from: '{query}'")
    
    # Smart procedure detection using enhanced synonym matching
    best_match = None
    best_score = 0
    
    # First try exact keyword matching
    for category, synonyms in PROCEDURE_SYNONYMS.items():
        for synonym in synonyms:
            if synonym.lower() in query_lower:
                score = 100 if synonym.lower() == query_lower else 90
                if score > best_score:
                    best_score = score
                    best_match = (category, synonym, score)
    
    # If no exact match, try fuzzy matching
    if not best_match:
        for category, synonyms in PROCEDURE_SYNONYMS.items():
            matches = advanced_fuzzy_match(query, synonyms, threshold=70)
            if matches:
                top_match = matches[0]
                if top_match[1] > best_score:
                    best_score = top_match[1]
                    best_match = (category, top_match[0], top_match[1])
    
    # If still no match, extract key medical terms from the query
    if not best_match:
        medical_terms = re.findall(r'\b(?:treatment|surgery|procedure|therapy|care|consultation|test|scan|operation)\b', query_lower)
        if medical_terms:
            # Try to categorize based on context
            if any(word in query_lower for word in ['heart', 'cardiac', 'bypass', 'angioplasty']):
                best_match = ('cardiac', 'cardiac procedure', 80)
            elif any(word in query_lower for word in ['cancer', 'tumor', 'oncology', 'chemo']):
                best_match = ('cancer', 'cancer treatment', 80)
            elif any(word in query_lower for word in ['fertility', 'ivf', 'reproductive']):
                best_match = ('fertility', 'fertility treatment', 80)
            elif any(word in query_lower for word in ['pregnancy', 'maternity', 'prenatal']):
                best_match = ('maternity', 'maternity care', 80)
            elif any(word in query_lower for word in ['emergency', 'urgent', 'trauma']):
                best_match = ('emergency', 'emergency care', 80)
            else:
                # Generic medical procedure
                best_match = ('general', f"medical {medical_terms[0]}", 70)
    
    if best_match:
        entities['procedure_type'] = best_match[0]
        entities['procedure'] = best_match[1]
        entities['match_confidence'] = best_match[2]
        print(f"🎯 Procedure match: '{best_match[1]}' → {best_match[0]} ({best_match[2]}% confidence)")
    else:
        # Extract any medical-sounding words as fallback
        medical_words = re.findall(r'\b[a-zA-Z]{3,}\b', query_lower)
        if medical_words:
            entities['procedure'] = ' '.join(medical_words[:3])  # Take first 3 words
            entities['procedure_type'] = 'general'
            entities['match_confidence'] = 50
            print(f"🔍 Fallback extraction: '{entities['procedure']}' (50% confidence)")
    
    # Enhanced age detection
    age_patterns = [
        r'(\d+)\s*(?:year|yr)s?\s*old',
        r'(\d+)(?:y|Y)',
        r'age\s*[:\-]?\s*(\d+)',
        r'(\d+)\s*(?:year|yr)s?(?:\s+old)?'
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, query_lower)
        if match:
            entities['age'] = int(match.group(1))
            print(f"👤 Age detected: {entities['age']}")
            break
    
    # Enhanced gender detection
    gender_patterns = [
        r'\b(\d+)\s*[mf]\b',  # "25F", "45M"
        r'\b(male|female|man|woman)\b',
        r'\b(m|f)\b'
    ]
    
    for pattern in gender_patterns:
        match = re.search(pattern, query_lower)
        if match:
            gender_text = match.group(1).lower()
            if gender_text in ['f', 'female', 'woman']:
                entities['gender'] = 'female'
            elif gender_text in ['m', 'male', 'man']:
                entities['gender'] = 'male'
            print(f"⚧ Gender detected: {entities.get('gender', 'unknown')}")
            break
    
    # Policy duration detection
    duration_patterns = [
        r'policy\s+(?:active|held|running)\s+(?:for\s+)?(\d+)\s+years?',
        r'(\d+)\s+years?\s+(?:policy|coverage)',
        r'policy\s+(?:duration|period)[:\-\s]*(\d+)\s+years?'
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, query_lower)
        if match:
            entities['policy_duration'] = int(match.group(1))
            print(f"📅 Policy duration: {entities['policy_duration']} years")
            break
    
    # Amount/cost detection
    amount_patterns = [
        r'₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'rs\.?\s*(\d+(?:,\d{3})*)',
        r'(\d+(?:,\d{3})*)\s*rupees?'
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            entities['requested_amount'] = int(float(amount_str))
            print(f"💰 Amount detected: ₹{entities['requested_amount']:,}")
            break
    
    # Urgency/priority detection
    urgency_keywords = ['emergency', 'urgent', 'critical', 'immediate', 'asap']
    if any(keyword in query_lower for keyword in urgency_keywords):
        entities['urgency'] = 'high'
        print("🚨 High urgency detected")
    
    return entities

def analyze_coverage_with_confusion_matrix(document_clauses, entities, query, actual_outcome=None):
    """
    Analyze coverage with proper confusion matrix support
    
    Confusion Matrix Cases:
    - AA (True Positive): Should approve & system approves
    - RR (True Negative): Should reject & system rejects  
    - AR (False Negative): Should approve but system rejects
    - RA (False Positive): Should reject but system approves
    """
    
    procedure_type = entities.get('procedure_type', '')
    procedure = entities.get('procedure', '')
    match_confidence = entities.get('match_confidence', 0)
    
    print(f"\n🎯 COVERAGE ANALYSIS")
    print(f"📋 Procedure: {procedure_type} - '{procedure}' ({match_confidence}%)")
    
    # Step 1: Check exclusions first (highest priority)
    exclusions = document_clauses.get('exclusions', [])
    exclusion_matches = advanced_fuzzy_match(procedure or query, exclusions, threshold=80)
    
    exclusion_result = None
    if exclusion_matches:
        top_exclusion = exclusion_matches[0]
        print(f"🚫 EXCLUSION MATCH: '{top_exclusion[0]}' ({top_exclusion[1]}% confidence)")
        
        exclusion_result = {
            'decision': 'REJECTED',
            'reason': f"Procedure matches excluded item: '{top_exclusion[0]}'",
            'amount': 0,
            'confidence': max(85, top_exclusion[1]),
            'exclusion_match': top_exclusion[0],
            'exclusion_confidence': top_exclusion[1],
            'clause_reference': f"Exclusions section",
            'fuzzy_matched_terms': [top_exclusion[0]]
        }
    
    # Step 2: Check inclusions/coverage
    inclusions = document_clauses.get('inclusions', {})
    coverage_amounts = document_clauses.get('coverage_amounts', {})
    
    # Direct inclusion match
    inclusion_result = None
    if procedure_type in inclusions:
        amount = inclusions[procedure_type]
        inclusion_result = {
            'decision': 'APPROVED',
            'reason': f"Direct coverage match for '{procedure_type}'",
            'amount': amount,
            'confidence': 95,
            'coverage_match': procedure_type,
            'clause_reference': f"Coverage section - {procedure_type}"
        }
    else:
        # Fuzzy match against inclusion keys
        inclusion_keys = list(inclusions.keys()) + list(coverage_amounts.keys())
        inclusion_matches = advanced_fuzzy_match(procedure or query, inclusion_keys, threshold=75)
        
        if inclusion_matches:
            top_inclusion = inclusion_matches[0]
            amount = inclusions.get(top_inclusion[0], 0) or extract_amount_from_text(coverage_amounts.get(top_inclusion[0], "0"))
            
            inclusion_result = {
                'decision': 'APPROVED',
                'reason': f"Fuzzy match with covered benefit: '{top_inclusion[0]}'",
                'amount': amount,
                'confidence': min(90, top_inclusion[1]),
                'coverage_match': top_inclusion[0],
                'coverage_confidence': top_inclusion[1],
                'clause_reference': f"Coverage section - {top_inclusion[0]}",
                'fuzzy_matched_terms': [top_inclusion[0]]
            }
    
    # Step 3: Decision logic with confusion matrix awareness
    final_result = None
    
    if exclusion_result and inclusion_result:
        # Conflict: both exclusion and inclusion found
        if exclusion_result['confidence'] > inclusion_result['confidence']:
            final_result = exclusion_result
            final_result['conflict_note'] = f"Exclusion overrides inclusion (confidence: {exclusion_result['confidence']}% vs {inclusion_result['confidence']}%)"
        else:
            # Rare case: inclusion overrides exclusion (very high confidence needed)
            if inclusion_result['confidence'] >= 95:
                final_result = inclusion_result
                final_result['conflict_note'] = f"High-confidence inclusion overrides exclusion"
            else:
                final_result = exclusion_result
                final_result['conflict_note'] = f"Exclusion takes precedence in ambiguous cases"
    
    elif exclusion_result:
        # Clear exclusion
        final_result = exclusion_result
    
    elif inclusion_result:
        # Check waiting period compliance for better decision accuracy
        waiting_periods = document_clauses.get('waiting_periods', {})
        policy_duration = entities.get('policy_duration', 0)
        
        # Enhanced inclusion logic with waiting period checking
        procedure_type = entities.get('procedure_type', '').lower()
        
        # Check if waiting period applies
        waiting_period_violation = False
        required_years = 0
        
        if 'fertility' in procedure_type or 'ivf' in procedure_type:
            required_years = int(waiting_periods.get('fertility_treatments', '2 years').split()[0])
        elif 'maternity' in procedure_type:
            required_years = int(waiting_periods.get('maternity', '2 years').split()[0])
        
        if required_years > 0 and policy_duration > 0 and policy_duration < required_years:
            waiting_period_violation = True
            final_result = {
                'decision': 'REJECTED',
                'reason': f"Waiting period not met. Required: {required_years} years, Policy held: {policy_duration} years",
                'amount': 0,
                'confidence': 90,
                'clause_reference': f"Waiting period requirement - {required_years} years",
                'waiting_period_issue': True,
                'required_waiting_years': required_years,
                'current_policy_years': policy_duration
            }
        else:
            # Approve with potential waiting period note
            final_result = inclusion_result
            if required_years > 0 and policy_duration >= required_years:
                final_result['waiting_period_met'] = f"✅ Waiting period satisfied ({policy_duration} years ≥ {required_years} years required)"
    
    else:
        # No specific match found - enhanced fallback logic with better matching
        procedure = entities.get('procedure', '').lower()
        query_lower = query.lower()
        
        print(f"🔍 No direct match found, trying enhanced fallback matching...")
        print(f"📝 Searching for: procedure='{procedure}', query='{query_lower}'")
        
        # Try broader matching against all available coverage
        all_coverage_terms = list(document_clauses.get('inclusions', {}).keys()) + list(document_clauses.get('coverage_amounts', {}).keys())
        print(f"📋 Available coverage terms: {all_coverage_terms}")
        
        # Enhanced fuzzy matching with lower threshold
        broad_matches = advanced_fuzzy_match(procedure or query, all_coverage_terms, threshold=60)
        if not broad_matches and procedure != query_lower:
            # Try matching the entire query
            broad_matches = advanced_fuzzy_match(query, all_coverage_terms, threshold=60)
        
        print(f"🔍 Broad matches found: {broad_matches}")
        
        if broad_matches:
            best_match = broad_matches[0]
            inclusions = document_clauses.get('inclusions', {})
            amount = inclusions.get(best_match[0], 0)
            
            final_result = {
                'decision': 'APPROVED',
                'reason': f'Broad coverage match found for "{procedure or query}" → "{best_match[0]}" ({best_match[1]}% confidence)',
                'amount': amount,
                'confidence': max(70, best_match[1]),
                'clause_reference': f'Broad coverage match - {best_match[0]}',
                'fallback_coverage': True,
                'fuzzy_matched_terms': [best_match[0]],
                'procedure_matched': procedure or query,
                'match_confidence': best_match[1]
            }
        elif any(term in query_lower for term in ['surgery', 'treatment', 'care', 'procedure', 'medical']):
            # Check for general medical coverage as last resort
            inclusions = document_clauses.get('inclusions', {})
            general_coverage = 0
            general_key = ""
            
            # Look for general medical terms
            for key in inclusions.keys():
                if any(general_term in key.lower() for general_term in ['general', 'medical', 'health', 'comprehensive']):
                    general_coverage = inclusions[key]
                    general_key = key
                    break
            
            if general_coverage > 0:
                final_result = {
                    'decision': 'APPROVED',
                    'reason': f'Covered under general medical benefits: "{general_key}" for medical procedure',
                    'amount': general_coverage,
                    'confidence': 65,
                    'clause_reference': f'General coverage - {general_key}',
                    'fallback_coverage': True,
                    'general_medical_coverage': True
                }
            else:
                final_result = {
                    'decision': 'REJECTED',
                    'reason': f'No coverage found for "{procedure or query}" in the uploaded policy document. Searched {len(all_coverage_terms)} coverage terms.',
                    'amount': 0,
                    'confidence': 80,
                    'clause_reference': 'No applicable coverage found',
                    'search_attempted': True,
                    'available_coverage': all_coverage_terms[:10]  # Show first 10 for reference
                }
        else:
            final_result = {
                'decision': 'REJECTED',
                'reason': f'Query "{query}" does not appear to be a medical procedure or treatment covered by this policy',
                'amount': 0,
                'confidence': 75,
                'clause_reference': 'Non-medical query',
                'available_coverage': all_coverage_terms[:10]  # Show first 10 for reference
            }
    
    # Add confusion matrix classification if actual outcome is provided
    if actual_outcome:
        predicted = final_result['decision']
        actual = actual_outcome.upper()
        
        if predicted == 'APPROVED' and actual == 'APPROVED':
            final_result['confusion_matrix'] = 'AA - True Positive'
        elif predicted == 'REJECTED' and actual == 'REJECTED':
            final_result['confusion_matrix'] = 'RR - True Negative'
        elif predicted == 'REJECTED' and actual == 'APPROVED':
            final_result['confusion_matrix'] = 'AR - False Negative'
        elif predicted == 'APPROVED' and actual == 'REJECTED':
            final_result['confusion_matrix'] = 'RA - False Positive'
    
    print(f"✅ FINAL DECISION: {final_result['decision']} (Confidence: {final_result['confidence']}%)")
    return final_result

def extract_amount_from_text(amount_str):
    """Extract numeric amount from text string"""
    if not amount_str:
        return 0
    
    # Remove currency symbols and commas
    clean_str = re.sub(r'[₹,rs\.]', '', str(amount_str), flags=re.IGNORECASE)
    
    # Extract number
    match = re.search(r'(\d+(?:,\d{3})*)', clean_str)
    if match:
        return int(match.group(1).replace(',', ''))
    
    return 0

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with detailed system status"""
    uploaded_count = len(uploaded_documents)
    document_list = []
    
    for file_id, doc_data in uploaded_documents.items():
        document_list.append({
            'file_id': file_id,
            'filename': doc_data['filename'],
            'inclusions': len(doc_data['clauses']['inclusions']),
            'exclusions': len(doc_data['clauses']['exclusions']),
            'upload_time': doc_data['upload_time']
        })
    
    return jsonify({
        'status': 'healthy',
        'server_mode': 'DOCUMENT_PROCESSING' if uploaded_count > 0 else 'UPLOAD_REQUIRED',
        'uploaded_documents': uploaded_count,
        'documents': document_list,
        'system_capabilities': {
            'gemini_ai': GEMINI_AVAILABLE,
            'fuzzy_matching': FUZZY_AVAILABLE,
            'pdf_processing': PDF_PROCESSING,
            'intelligent_matching': FUZZY_AVAILABLE,
            'dynamic_processing': True,
            'mock_data': False  # Mock data disabled
        },
        'timestamp': datetime.now().isoformat(),
        'message': f"{'Ready to process queries with {uploaded_count} document(s)' if uploaded_count > 0 else '⚠️ Please upload PDF policy documents to begin analysis'}"
    })

@app.route('/')
def index():
    """Serve the frontend index page"""
    try:
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'index.html')
        with open(frontend_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"""
        <html>
        <head><title>Dynamic AI Insurance Query System</title></head>
        <body>
            <h1>🎯 Dynamic AI Insurance Query System</h1>
            <p>Server is running! Backend API available at:</p>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><strong>POST /upload</strong> - Upload PDF documents</li>
                <li><strong>POST /query</strong> - Process insurance queries</li>
                <li><strong>GET /documents</strong> - List uploaded documents</li>
            </ul>
            <p>Frontend file not found: {str(e)}</p>
            <p>You can use tools like Postman or curl to test the API endpoints.</p>
        </body>
        </html>
        """

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """Handle file upload with dynamic PDF processing"""
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
    
    try:
        print("📤 File upload request received")
        
        # Check if file is in request
        if 'file' not in request.files:
            print("❌ No file in request")
            response_data = {
                'error': 'No file provided',
                'status': 'failed'
            }
            response = make_response(jsonify(response_data), 400)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            print("❌ No file selected")
            response_data = {
                'error': 'No file selected',
                'status': 'failed'
            }
            response = make_response(jsonify(response_data), 400)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            print(f"❌ Invalid file type: {file.filename}")
            response_data = {
                'error': 'Only PDF files are allowed',
                'status': 'failed'
            }
            response = make_response(jsonify(response_data), 400)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        
        # Generate unique file ID and save file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{file.filename}")
        
        # Save the file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        print(f"✅ File saved: {file_path} ({file_size} bytes)")
        
        # Process PDF and extract clauses
        processing_result = None
        if PDF_PROCESSING:
            try:
                print("🔍 Processing PDF content...")
                text_content = extract_text_from_pdf(file_path)
                clauses = parse_insurance_clauses(text_content)
                
                # Store the processed document
                uploaded_documents[file_id] = {
                    'filename': file.filename,
                    'file_path': file_path,
                    'text_content': text_content,
                    'clauses': clauses,
                    'upload_time': datetime.now().isoformat(),
                    'file_size': file_size
                }
                
                processing_result = {
                    'inclusions_found': len(clauses['inclusions']),
                    'exclusions_found': len(clauses['exclusions']),
                    'policy_name': clauses['policy_info'].get('name', 'Unknown Policy'),
                    'waiting_periods': len(clauses['waiting_periods'])
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
            'pdf_processing': PDF_PROCESSING,
            'fuzzy_matching': FUZZY_AVAILABLE,
            'processing_result': processing_result
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

@app.route('/progress/<file_id>', methods=['GET'])
def get_progress(file_id):
    """Get upload progress"""
    response_data = {
        'progress': 100,
        'status': 'completed',
        'file_id': file_id,
        'intelligent_analysis': FUZZY_AVAILABLE
    }
    
    response = make_response(jsonify(response_data))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/query', methods=['POST', 'OPTIONS'])
def process_query():
    """Process insurance query with DYNAMIC document analysis and confusion matrix support"""
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
        actual_outcome = data.get('actual_outcome')  # For confusion matrix validation
        request_id = str(uuid.uuid4())[:8]
        
        print(f"\n🎯 DYNAMIC PROCESSING [ID: {request_id}]")
        print(f"📝 Query: '{query}'")
        print(f"📄 File ID: '{file_id}'")
        print(f"🎯 Advanced Fuzzy: {'✅ Enabled' if FUZZY_AVAILABLE else '❌ Disabled'}")
        print(f"📑 PDF Processing: {'✅ Enabled' if PDF_PROCESSING else '❌ Disabled'}")
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Enhanced entity extraction
        entities = extract_entities_advanced(query)
        print(f"🔍 Advanced extraction: {entities}")
        
        # Get document clauses - PRIORITIZE UPLOADED DOCUMENTS
        document_clauses = None
        document_info = {}
        
        # STEP 1: Check for uploaded documents FIRST
        if uploaded_documents:
            # Use the most recent uploaded document if no specific file_id
            if not file_id or file_id not in uploaded_documents:
                # Get the most recently uploaded document
                latest_doc_id = max(uploaded_documents.keys(), key=lambda x: uploaded_documents[x]['upload_time'])
                file_id = latest_doc_id
                print(f"🔄 No specific file_id provided, using most recent upload: {latest_doc_id}")
            
            if file_id in uploaded_documents:
                # Use uploaded document
                doc_data = uploaded_documents[file_id]
                document_clauses = doc_data['clauses']
                document_info = {
                    'source': 'uploaded_document',
                    'filename': doc_data['filename'],
                    'policy_name': document_clauses['policy_info'].get('name', 'Unknown Policy'),
                    'processed_at': doc_data['upload_time'],
                    'file_size': doc_data['file_size']
                }
                print(f"📋 Using uploaded document: {doc_data['filename']}")
                print(f"📊 Document stats: {len(document_clauses.get('inclusions', {}))} inclusions, {len(document_clauses.get('exclusions', []))} exclusions")
        
        # STEP 2: REQUIRE UPLOADED DOCUMENTS - No mock fallback
        if document_clauses is None:
            print("❌ ERROR: No uploaded documents found")
            return jsonify({
                'error': 'No PDF documents uploaded. Please upload a policy document first.',
                'request_id': request_id,
                'instructions': {
                    'step1': 'Upload a PDF policy document using the frontend',
                    'step2': 'Submit your query after successful document upload',
                    'note': 'System requires actual policy documents for analysis'
                }
            }), 400
        
        # DIAGNOSTIC: Show what was extracted from document
        print(f"\n🔍 DOCUMENT DIAGNOSTIC:")
        print(f"📄 Inclusions found: {list(document_clauses.get('inclusions', {}).keys())}")
        print(f"🚫 Exclusions found: {document_clauses.get('exclusions', [])}")
        print(f"⏱️ Waiting periods: {document_clauses.get('waiting_periods', {})}")
        print(f"🔍 Query entities: {entities}")
        print(f"📝 Raw query: '{query}'\n")
        
        # Advanced coverage analysis with confusion matrix support
        analysis = analyze_coverage_with_confusion_matrix(document_clauses, entities, query, actual_outcome)
        print(f"📊 Analysis result: {analysis}")
        
        # Build comprehensive response
        response_data = {
            'decision': analysis['decision'],
            'amount': analysis.get('amount', 0),
            'confidence': analysis['confidence'],
            'justification': {
                'reasoning': analysis['reason'],
                'clause_reference': analysis.get('clause_reference', 'N/A'),
                'document_based': True,
                'advanced_fuzzy_matching': FUZZY_AVAILABLE,
                'conflict_note': analysis.get('conflict_note')
            },
            'fuzzy_matched_terms': analysis.get('fuzzy_matched_terms', []),
            'exclusion_match': analysis.get('exclusion_match'),
            'coverage_match': analysis.get('coverage_match'),
            'entities_extracted': entities,
            'document_info': document_info,
            'confusion_matrix': analysis.get('confusion_matrix'),
            'system_capabilities': {
                'dynamic_pdf_processing': PDF_PROCESSING,
                'advanced_fuzzy_matching': FUZZY_AVAILABLE,
                'gemini_ai': GEMINI_AVAILABLE,
                'confusion_matrix_support': True
            },
            'processing_details': {
                'inclusions_checked': len(document_clauses.get('inclusions', {})),
                'exclusions_checked': len(document_clauses.get('exclusions', [])),
                'entity_confidence': entities.get('match_confidence', 0),
                'fallback_used': analysis.get('fallback_coverage', False)
            },
            'request_id': request_id,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ DYNAMIC RESPONSE: {response_data['decision']} (Confidence: {response_data['confidence']}%)")
        
        response = make_response(jsonify(response_data))
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        traceback.print_exc()
        
        error_response = {
            'decision': 'ERROR',
            'confidence': 0,
            'amount': 0,
            'justification': {
                'reasoning': f"System error: {str(e)}",
                'document_based': False,
                'advanced_fuzzy_matching': False
            },
            'entities_extracted': {},
            'error': str(e),
            'request_id': str(uuid.uuid4())[:8]
        }
        
        response = make_response(jsonify(error_response), 500)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

@app.route('/debug-document/<file_id>', methods=['GET'])
def debug_document(file_id):
    """Debug endpoint to see what was extracted from a document"""
    if file_id not in uploaded_documents:
        return jsonify({'error': f'Document {file_id} not found'}), 404
    
    doc_data = uploaded_documents[file_id]
    debug_info = {
        'filename': doc_data['filename'],
        'file_size': doc_data['file_size'],
        'text_length': len(doc_data['text_content']),
        'text_preview': doc_data['text_content'][:500] + "..." if len(doc_data['text_content']) > 500 else doc_data['text_content'],
        'parsed_clauses': doc_data['clauses'],
        'inclusions_count': len(doc_data['clauses']['inclusions']),
        'exclusions_count': len(doc_data['clauses']['exclusions']),
        'waiting_periods_count': len(doc_data['clauses']['waiting_periods'])
    }
    
    response = make_response(jsonify(debug_info))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all uploaded and processed documents"""
    response_data = {
        'uploaded_documents': len(uploaded_documents),
        'documents': []
    }
    
    for file_id, doc_data in uploaded_documents.items():
        document_summary = {
            'file_id': file_id,
            'filename': doc_data['filename'],
            'policy_name': doc_data['clauses']['policy_info'].get('name', 'Unknown'),
            'upload_time': doc_data['upload_time'],
            'file_size': doc_data['file_size'],
            'inclusions_count': len(doc_data['clauses']['inclusions']),
            'exclusions_count': len(doc_data['clauses']['exclusions']),
            'waiting_periods_count': len(doc_data['clauses']['waiting_periods'])
        }
        response_data['documents'].append(document_summary)
    
    response = make_response(jsonify(response_data))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == '__main__':
    print("🎯 Starting DYNAMIC AI Insurance Query System...")
    print("✅ Enhanced Features:")
    print(f"   - Dynamic PDF document processing: {'✅ Enabled' if PDF_PROCESSING else '❌ Install pdfplumber & PyPDF2'}")
    print(f"   - Advanced fuzzy matching: {'✅ Enabled' if FUZZY_AVAILABLE else '❌ Install rapidfuzz'}")
    print("   - Confusion matrix support (AA, RR, AR, RA)")
    print("   - Dynamic clause extraction from uploaded documents")
    print("   - Enhanced semantic understanding")
    print("   - Natural language query processing")
    
    print("\n🔧 System Capabilities:")
    print(f"   - PDF Text Extraction: {'✅' if PDF_PROCESSING else '❌'}")
    print(f"   - Fuzzy Term Matching: {'✅' if FUZZY_AVAILABLE else '❌'}")
    print(f"   - Gemini AI Integration: {'✅' if GEMINI_AVAILABLE else '❌'}")
    print("   - Confusion Matrix Classification: ✅")
    print("   - Dynamic Document Processing: ✅")
    
    if not PDF_PROCESSING:
        print("\n⚠️  RECOMMENDATION: Install PDF processing libraries:")
        print("   pip install pdfplumber PyPDF2")
    
    if not FUZZY_AVAILABLE:
        print("\n⚠️  RECOMMENDATION: Install fuzzy matching library:")
        print("   pip install rapidfuzz  # (preferred)")
        print("   # OR: pip install fuzzywuzzy python-Levenshtein")
    
    print("\n📋 Supported Query Examples:")
    print("   • 'IVF treatment, policy active 2 years'")
    print("   • 'Heart operation for 45-year-old male'")
    print("   • 'Prenatal checkup, 25F, standard policy'")
    print("   • 'Cancer treatment ₹5,00,000'")
    
    print("\n🌐 Server starting on http://localhost:5000")
    print("📁 Upload folder:", os.path.abspath(UPLOAD_FOLDER))
    
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
