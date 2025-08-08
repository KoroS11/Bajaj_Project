# 🎯 AI Insurance Query System - Real Document Analysis

## ⚡ IMPORTANT: UPLOAD YOUR DOCUMENTS FIRST

**🚨 NEW BEHAVIOR**: System now requires YOUR PDF policy documents - no mock data used!

### Method 1: Ultimate Easy (Recommended)
1. **Double-click** `ULTIMATE_STARTUP.bat`
2. **Wait** for "Server started" message
3. **Open browser** → navigate to `frontend/working_interface.html`
4. **📄 UPLOAD PDF** → Your insurance policy document first
5. **Submit query** → Analyze against YOUR document
6. **Done!** 🎉

### Method 2: Manual
1. Open terminal in project directory
2. Run: `venv_enhanced\Scripts\activate`
3. Run: `cd backend && python main_intelligent_fuzzy.py`
4. Open `frontend/working_interface.html`
5. **Upload your PDF policy document**
6. Submit queries for analysis

### ✅ Server Health Check
- Navigate to: http://localhost:5000/health
- Should show: `"server_mode": "UPLOAD_REQUIRED"` (before upload)
- Should show: `"server_mode": "DOCUMENT_PROCESSING"` (after upload)

### ✅ Frontend Interface
- Open: `frontend/working_interface.html`
- Should show "⚠️ Upload Required" status initially
- Should show green "Ready" status after PDF upload
- Upload area should be functional

### ✅ Document Upload Test
1. **Upload a PDF** insurance policy document
2. **Wait for processing** - should show success message
3. **Status should change** to "Ready | 1 document(s) loaded"
4. **Query box** should now be ready for use

### ✅ Real Document Query Test
1. **Submit query** based on your uploaded document: `"Coverage for [procedure in your document]"`
2. **Expected result**: Decision based on YOUR document's terms
3. **Coverage found**: APPROVED with amounts from your document  
4. **Coverage not found**: REJECTED with reasoning

## 🎯 Example Test Queries

**⚠️ Note**: Results depend entirely on YOUR uploaded document content!

```
"Heart surgery coverage" (check if your policy covers this)
"Cancer treatment benefits" (verify cancer coverage in your document)  
"Maternity care eligibility" (see maternity terms in your policy)
"Emergency medical treatment" (check emergency coverage)
"[Any procedure mentioned in your PDF]"
```

## 🔧 Troubleshooting

### Server Won't Start
- Check if port 5000 is available
- Run: `netstat -ano | findstr :5000`
- Kill conflicting process if found

### Virtual Environment Issues
- Delete `venv_enhanced` folder
- Run `ULTIMATE_STARTUP.bat` again (it will recreate)

### Frontend Not Loading
- Use `working_interface.html` (guaranteed to work)
- Check browser console for errors
- Ensure server is running first

### Dependencies Missing
- Run: `pip install Flask Flask-CORS rapidfuzz pdfplumber PyPDF2`
- Or use `ULTIMATE_STARTUP.bat` (handles automatically)

## 🎮 System Features

### 🧠 Smart Document Processing
- PDF text extraction with pdfplumber and PyPDF2
- Dynamic inclusion/exclusion detection
- Intelligent clause matching

### 🎯 Advanced Fuzzy Matching
- RapidFuzz integration for flexible term matching
- Medical terminology recognition
- Context-aware decision making

### 📊 Comprehensive Response Format
```json
{
    "decision": "APPROVED/REJECTED",
    "confidence": 85,
    "justification": {
        "reasoning": "Detailed explanation...",
        "clause_reference": "Policy section..."
    },
    "entities_extracted": {
        "procedure": "IVF treatment",
        "age": 30,
        "gender": "female"
    },
    "document_info": {
        "source": "uploaded_document/mock_data",
        "processing_method": "dynamic"
    }
}
```

## 🔄 Development Workflow

1. **Backend Changes**: Edit `backend/main_intelligent_fuzzy.py`
2. **Frontend Changes**: Edit `frontend/working_interface.html`
3. **Restart**: Use `ULTIMATE_STARTUP.bat` for clean restart
4. **Test**: Use health check and test queries

## 📁 Project Structure
```
bajaj_V3/
├── ULTIMATE_STARTUP.bat          # 🚀 Main startup script
├── backend/
│   ├── main_intelligent_fuzzy.py # 🧠 Core Flask application
│   └── uploads/                  # 📄 Uploaded PDFs
├── frontend/
│   ├── working_interface.html    # 🌐 Guaranteed working interface
│   └── index.html               # 🎨 Enhanced interface
└── venv_enhanced/               # 🐍 Python virtual environment
```

## 🎯 Success Indicators

### ✅ System Ready When You See:
- Server status: "Server Online" (green)
- Health endpoint returns: `"status": "healthy"`
- Upload area responsive to clicks
- Submit button functional
- Example queries work immediately

### ✅ Full Functionality Test:
1. Upload PDF → See processing confirmation
2. Submit query → Get structured response
3. Try multiple queries → Consistent results
4. Check server logs → No errors

---

**🎉 THAT'S IT! Your AI Insurance Query System is now running!**

For questions or issues, check the troubleshooting section above.
