# 🏆 HackRx Webhook Documentation

## Webhook URL for Submission

After deploying to Vercel, your webhook URL will be:

```
https://your-project-name.vercel.app/hackrx/run
```

Example:
```
https://bajaj-insurance-engine.vercel.app/hackrx/run
```

---

## 📍 Endpoint Details

### Main Webhook Endpoint
- **URL**: `/hackrx/run`
- **Methods**: `GET`, `POST`, `OPTIONS`
- **Purpose**: Receives and processes test requests from HackRx evaluation system

### Additional Endpoints
- **Health Check**: `/hackrx/health` (GET)
- **Test Runner**: `/hackrx/test` (POST)

---

## 🔧 Request Formats

### 1. Health Check (GET Request)
```http
GET https://your-app.vercel.app/hackrx/run
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-08T14:30:00",
  "service": "Bajaj Insurance Query Engine",
  "version": "1.0.0",
  "endpoints": ["/hackrx/run", "/query", "/upload", "/health"],
  "capabilities": {
    "pdf_processing": true,
    "nlp_analysis": true,
    "fuzzy_matching": true,
    "decision_engine": true
  }
}
```

### 2. Insurance Query (POST Request)
```http
POST https://your-app.vercel.app/hackrx/run
Content-Type: application/json

{
  "query": "25F with 2 years policy, need IVF treatment"
}
```

**Response:**
```json
{
  "status": "success",
  "query": "25F with 2 years policy, need IVF treatment",
  "decision": "REJECTED",
  "amount": 0,
  "confidence": 95,
  "justification": "Excluded: ivf treatment",
  "confusion_matrix": "RR",
  "extracted_info": {
    "age": 25,
    "gender": "female",
    "procedure": "IVF",
    "policy_duration": "2 years"
  },
  "policy_type": "Standard Policy",
  "timestamp": "2024-01-08T14:30:00"
}
```

### 3. Multiple Test Cases
```http
POST https://your-app.vercel.app/hackrx/run
Content-Type: application/json

{
  "type": "test",
  "test_cases": [
    {"query": "45M requiring cardiac surgery"},
    {"query": "30F pregnant, maternity benefits?"},
    {"query": "Emergency treatment coverage"}
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "tests_run": 3,
  "results": [
    {
      "test": "45M requiring cardiac surgery",
      "result": {
        "status": "success",
        "decision": "APPROVED",
        "amount": 500000,
        "confidence": 95,
        "justification": "Covered under: cardiac surgery"
      }
    },
    // ... more results
  ],
  "timestamp": "2024-01-08T14:30:00"
}
```

### 4. Policy Upload
```http
POST https://your-app.vercel.app/hackrx/run
Content-Type: application/json

{
  "type": "policy_upload",
  "policy_text": "Coverage: Cardiac Surgery: ₹1000000...",
  "policy_type": "premium"
}
```

**Response:**
```json
{
  "status": "success",
  "session_id": "hackrx_1234567890",
  "policy_processed": true,
  "inclusions_found": 5,
  "exclusions_found": 3
}
```

---

## 📊 Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Missing or invalid parameters |
| 500 | Server Error | Internal processing error |

---

## 🎯 Features Supported

### ✅ Query Processing
- Natural language understanding
- Age and gender extraction
- Procedure identification
- Policy duration parsing

### ✅ Decision Engine
- APPROVED/REJECTED decisions
- Coverage amount calculation
- Confidence scoring (0-100%)
- Justification messages

### ✅ Confusion Matrix Classification
- **RR**: Correctly Rejected (True Negative)
- **AA**: Correctly Approved (True Positive)
- **RA**: Incorrectly Approved (False Positive)
- **AR**: Incorrectly Rejected (False Negative)

### ✅ Policy Types
- Standard Policy
- Fertility Policy
- Premium Policy

### ✅ Supported Procedures
- IVF/Fertility treatments
- Cardiac surgery
- Maternity benefits
- Emergency treatment
- General medical
- Diagnostic tests
- Hospitalization

---

## 🧪 Testing the Webhook

### Local Testing
```bash
# Start the server
python api/hackrx.py

# Test with curl
curl http://localhost:5000/hackrx/run

# Test with Python script
python test_hackrx.py
```

### Production Testing
```bash
# Test deployed endpoint
curl https://your-app.vercel.app/hackrx/run

# Test with POST request
curl -X POST https://your-app.vercel.app/hackrx/run \
  -H "Content-Type: application/json" \
  -d '{"query": "25F need IVF treatment"}'
```

---

## 🚀 Deployment Steps

1. **Deploy to Vercel:**
   ```bash
   vercel --prod
   ```

2. **Get your webhook URL:**
   ```
   https://[your-project-name].vercel.app/hackrx/run
   ```

3. **Test the endpoint:**
   ```bash
   python test_hackrx.py
   ```

4. **Submit to HackRx:**
   - Use the full URL including `/hackrx/run`
   - Example: `https://bajaj-insurance-engine.vercel.app/hackrx/run`

---

## 📝 Sample Test Queries

### Test Query 1: IVF Treatment
```json
{
  "query": "I am a 25-year-old female with 2 years active policy. Is IVF treatment covered?"
}
```
Expected: REJECTED (Standard policy excludes IVF)

### Test Query 2: Cardiac Surgery
```json
{
  "query": "45M requiring cardiac surgery"
}
```
Expected: APPROVED (Covered with amount)

### Test Query 3: Maternity
```json
{
  "query": "30F pregnant, need maternity benefits"
}
```
Expected: APPROVED/REJECTED (Depends on policy type)

### Test Query 4: Emergency
```json
{
  "query": "Emergency treatment coverage amount?"
}
```
Expected: APPROVED (Usually covered)

---

## ⚙️ Configuration

The webhook is configured in `vercel.json`:
```json
{
  "routes": [
    {
      "src": "/hackrx/run",
      "dest": "api/hackrx.py"
    },
    {
      "src": "/hackrx/(.*)",
      "dest": "api/hackrx.py"
    }
  ]
}
```

---

## 🔒 Security

- ✅ CORS enabled for cross-origin requests
- ✅ Input validation and sanitization
- ✅ Error handling with proper status codes
- ✅ No sensitive data in responses

---

## 📞 Support

If you encounter issues:
1. Check the health endpoint: `/hackrx/health`
2. Review logs in Vercel dashboard
3. Test with the provided test script
4. Ensure all dependencies are in `requirements.txt`

---

## ✨ Key Advantages

1. **No Database Required** - Works with in-memory storage
2. **Flexible Input** - Accepts various query formats
3. **Comprehensive Response** - Includes all required fields
4. **Fast Processing** - Serverless architecture
5. **Reliable** - Error handling and fallbacks

---

## 📋 Submission Checklist

Before submitting to HackRx:

- [x] Webhook endpoint created (`/hackrx/run`)
- [x] Supports GET requests (health check)
- [x] Supports POST requests (queries)
- [x] Returns JSON responses
- [x] Handles errors gracefully
- [x] Deployed to Vercel
- [x] Tested with various queries
- [x] URL format correct: `https://your-app.vercel.app/hackrx/run`

---

**Your Webhook URL for HackRx:**
```
https://bajaj-insurance-engine.vercel.app/hackrx/run
```

This URL is ready to receive and process test requests from the HackRx evaluation system! 🎉
