# 🧪 Testing Guide - Before Deployment

This guide will help you test both APIs before deploying to Vercel.

## 📋 Quick Test Process

### Step 1: Test the Vercel-Compatible API (No Database Required!)

1. **Start the server**:
   - Double-click `start_vercel_api.bat`
   - OR run: `python api/vercel_index.py`

2. **Open the frontend**:
   - Open `index.html` in your browser
   - The URL should be: `file:///C:/Users/rupga/OneDrive/Desktop/8/Bajaj_Project/index.html`

3. **Test the features**:
   - ✅ **Without PDF**: Click sample queries and submit (uses default policies)
   - ✅ **With PDF**: Upload a policy PDF, then submit queries
   - ✅ **Check results**: Verify APPROVED/REJECTED decisions

### Step 2: Test the Original API

1. **Stop the Vercel API** (Press Ctrl+C in the command window)

2. **Start the original server**:
   - Double-click `start_original_api.bat`
   - OR run: `python api/index.py`

3. **Test with the same frontend**:
   - Refresh the browser page
   - Test the same features

### Step 3: Run Automated Tests

1. **Keep one API running** (either one)

2. **Open a new terminal** and run:
   ```bash
   python test_apis.py
   ```

3. **Follow the prompts** to test each API

## 🔍 What to Check

### ✅ Vercel API Should:
- Work WITHOUT any database
- Process PDFs in memory
- Handle queries with default policies
- Return proper JSON responses
- Show confidence scores and classifications

### ✅ Original API Should:
- Have all the same features
- Work with uploaded PDFs
- Process complex queries

## 📊 Test Scenarios

### Scenario 1: No PDF Upload
```
Query: "25F with 2 years policy, need IVF treatment"
Expected: REJECTED (Standard policy doesn't cover IVF)
```

### Scenario 2: With PDF Upload
```
1. Upload a policy PDF
2. Query: "Is cardiac surgery covered?"
Expected: Decision based on PDF content
```

### Scenario 3: Multiple Queries
```
- "45M requiring cardiac surgery" → Should detect cardiac procedure
- "30F pregnant, maternity benefits?" → Should detect maternity
- "Emergency treatment coverage" → Should detect emergency
```

## 🌐 API Endpoints to Test

### Health Check
```
GET http://localhost:5000/health
```
Should return:
- Status: healthy
- Capabilities list
- Message

### Query Processing
```
POST http://localhost:5000/query
Body: {
  "query": "Your question here",
  "session_id": "optional_if_pdf_uploaded"
}
```

### PDF Upload (Vercel API)
```
POST http://localhost:5000/upload
Body: Form-data with PDF file
```

## 🎯 Success Criteria

Your project is ready for deployment when:

1. ✅ Health check returns "healthy"
2. ✅ Queries work without PDF upload
3. ✅ PDF upload processes successfully
4. ✅ Queries return proper decisions (APPROVED/REJECTED)
5. ✅ Confidence scores are shown
6. ✅ Frontend displays results correctly

## 🚀 Ready to Deploy?

If all tests pass:

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel
   ```

3. **Follow prompts** and your app will be live!

## 🐛 Common Issues & Solutions

### Issue: "Connection refused"
**Solution**: Make sure the API server is running

### Issue: "No module named 'flask'"
**Solution**: Install dependencies: `pip install -r requirements.txt`

### Issue: "PDF processing not available"
**Solution**: Install: `pip install pdfplumber PyPDF2`

### Issue: Frontend not connecting to API
**Solution**: Check if API is running on port 5000

## 📝 Testing Checklist

- [ ] Vercel API starts successfully
- [ ] Health endpoint works
- [ ] Query without PDF works
- [ ] PDF upload works
- [ ] Query with PDF works
- [ ] Frontend displays results
- [ ] Confidence scores shown
- [ ] Decision classifications correct
- [ ] Original API also works
- [ ] Automated tests pass

## 💡 Tips

1. **Test locally first** - Always test before deploying
2. **Check console** - Browser console shows errors
3. **Use test script** - `python test_apis.py` for automated testing
4. **Test both APIs** - Ensure both work before choosing one
5. **Check logs** - Server logs show processing details

---

Once everything works locally, you're ready to deploy to Vercel! 🎉
