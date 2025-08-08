#!/usr/bin/env python3
"""
Quick validation script to test the enhanced system
"""

def test_imports():
    """Test if all required imports work"""
    try:
        import rapidfuzz
        print("✅ rapidfuzz imported successfully")
    except ImportError as e:
        print(f"❌ rapidfuzz import failed: {e}")
    
    try:
        import pdfplumber
        print("✅ pdfplumber imported successfully")
    except ImportError as e:
        print(f"❌ pdfplumber import failed: {e}")
    
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF2 import failed: {e}")
    
    try:
        import flask
        from flask_cors import CORS
        print("✅ Flask and CORS imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")

def test_fuzzy_matching():
    """Test fuzzy matching functionality"""
    try:
        from rapidfuzz import fuzz
        
        # Test fuzzy matching
        query = "fertility treatment"
        target = "infertility consultation"
        score = fuzz.ratio(query, target)
        
        print(f"🧠 Fuzzy match test:")
        print(f"   Query: '{query}'")
        print(f"   Target: '{target}'")
        print(f"   Score: {score}%")
        
        if score >= 85:
            print("✅ High confidence match!")
        else:
            print("⚠️ Low confidence match")
            
    except Exception as e:
        print(f"❌ Fuzzy matching test failed: {e}")

def test_entity_extraction():
    """Test entity extraction"""
    import re
    
    test_queries = [
        "IVF treatment, policy active 2 years",
        "Heart surgery for 45-year-old male", 
        "Prenatal checkup, 25F, standard policy"
    ]
    
    print("🔍 Entity extraction test:")
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        
        # Age detection
        age_match = re.search(r'(\d+)\s*(?:year|yr)s?\s*old|(\d+)[mfMF]', query.lower())
        if age_match:
            age = age_match.group(1) or age_match.group(2)
            print(f"   👤 Age: {age}")
        
        # Policy duration
        duration_match = re.search(r'policy\s+active\s+(\d+)\s+years?', query.lower())
        if duration_match:
            duration = duration_match.group(1)
            print(f"   📅 Duration: {duration} years")
        
        # Gender
        gender_match = re.search(r'(\d+)[mf]|male|female', query.lower())
        if gender_match:
            gender_text = gender_match.group(0)
            if 'f' in gender_text or 'female' in gender_text:
                print(f"   ⚧ Gender: female")
            elif 'm' in gender_text or 'male' in gender_text:
                print(f"   ⚧ Gender: male")

if __name__ == "__main__":
    print("🎯 ENHANCED SYSTEM VALIDATION")
    print("=" * 40)
    
    print("\n1. Testing imports...")
    test_imports()
    
    print("\n2. Testing fuzzy matching...")
    test_fuzzy_matching()
    
    print("\n3. Testing entity extraction...")
    test_entity_extraction()
    
    print("\n✅ Validation complete!")
    print("\nTo start the server:")
    print("   python main_intelligent_fuzzy.py")
