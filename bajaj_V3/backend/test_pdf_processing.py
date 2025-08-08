#!/usr/bin/env python3
"""
Quick test script to verify PDF processing works correctly
"""
import os
import sys

# Test PDF processing libraries
try:
    import pdfplumber
    import PyPDF2
    print("✅ PDF processing libraries imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_pdf_processing():
    uploads_dir = 'uploads'
    
    if not os.path.exists(uploads_dir):
        print(f"❌ {uploads_dir} directory not found")
        return False
    
    pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in uploads directory")
        return False
    
    # Test with first PDF
    test_file = pdf_files[0]
    file_path = os.path.join(uploads_dir, test_file)
    
    print(f"🔍 Testing PDF processing with: {test_file}")
    print(f"📄 File size: {os.path.getsize(file_path)} bytes")
    
    # Test pdfplumber
    try:
        with pdfplumber.open(file_path) as pdf:
            text_content = ""
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
                if i == 0:  # Show first page sample
                    print(f"📝 First page sample (first 200 chars):")
                    print(f"'{page_text[:200]}...'")
            
            print(f"✅ pdfplumber extracted {len(text_content)} characters from {len(pdf.pages)} pages")
            
            # Check for common insurance terms
            text_lower = text_content.lower()
            insurance_terms = ['covered', 'exclusion', 'policy', 'premium', 'claim', 'benefit']
            found_terms = [term for term in insurance_terms if term in text_lower]
            print(f"🔍 Found insurance terms: {found_terms}")
            
            return True
            
    except Exception as e:
        print(f"❌ pdfplumber failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 PDF Processing Test")
    print("=" * 40)
    
    success = test_pdf_processing()
    
    if success:
        print("\n✅ PDF processing test PASSED")
    else:
        print("\n❌ PDF processing test FAILED")
        sys.exit(1)
