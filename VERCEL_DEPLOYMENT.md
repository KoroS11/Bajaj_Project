# 🚀 Vercel Deployment Guide

This guide will help you deploy your Bajaj Insurance Query Engine to Vercel without needing a database.

## 📋 Prerequisites

1. A [Vercel account](https://vercel.com/signup) (free)
2. [Git](https://git-scm.com/) installed on your machine
3. [Node.js](https://nodejs.org/) installed (for Vercel CLI)

## 🎯 How It Works Without a Database

Your project will work perfectly on Vercel without a database:

- **PDF Processing**: PDFs are processed in-memory during the session
- **Session Storage**: Document data is stored temporarily in memory for the current session
- **Default Policies**: If no PDF is uploaded, the system uses pre-configured sample policies
- **Stateless Operation**: Each request is independent, perfect for serverless

## 📦 Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy the project**:
   ```bash
   cd Bajaj_Project
   vercel
   ```

4. **Follow the prompts**:
   - Choose your account
   - Link to existing project or create new
   - Accept default settings

5. **Deploy to production**:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via GitHub

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Connect to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Click "Deploy"

## 🔧 Configuration

### Environment Variables (Optional)

If you want to enable persistent storage, add these in Vercel Dashboard > Settings > Environment Variables:

1. **BLOB_READ_WRITE_TOKEN** (Optional)
   - Enables Vercel Blob Storage for persistent PDF storage
   - Get it from Vercel Dashboard > Storage > Create Database > Blob

2. **GOOGLE_API_KEY** (Optional)
   - For enhanced AI features with Google Gemini
   - Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🌟 Features That Work Without Database

✅ **PDF Upload & Processing**
- Users can upload PDF policy documents
- Documents are processed in real-time
- Text extraction and clause identification

✅ **Query Processing**
- Natural language query understanding
- Age, gender, and procedure extraction
- Fuzzy matching for better accuracy

✅ **Coverage Analysis**
- Automatic decision making (APPROVED/REJECTED)
- Confidence scores
- Confusion matrix classification (RR, RA, AR, AA)

✅ **Sample Policies**
- Pre-configured policies (Standard, Fertility, Premium)
- Works even without PDF upload
- Good for testing and demos

## 📱 Using Your Deployed App

1. **Access your app**: 
   - Production: `https://your-project.vercel.app`
   - Preview: Each commit gets a unique URL

2. **Upload a PDF** (Optional):
   - Click "Choose File" and select a policy PDF
   - The system will extract and process the information

3. **Ask Questions**:
   - Type natural language queries
   - Example: "25F with 2 years policy, is IVF covered?"
   - Click "Analyze Coverage"

4. **View Results**:
   - See APPROVED/REJECTED decision
   - Coverage amount (if applicable)
   - Confidence score and classification

## 🔍 How Session Storage Works

Since we're not using a database, here's how the app manages data:

1. **PDF Upload**: 
   - PDF is processed immediately
   - Extracted data stored in memory with a session ID
   - Session ID returned to frontend

2. **Query Processing**:
   - Frontend sends query + session ID
   - Backend retrieves document data from memory
   - Processes query against the document

3. **Limitations**:
   - Data persists only during the session
   - Serverless functions may reset after inactivity
   - Each deployment creates fresh instance

## 💡 Tips for Production

1. **Performance**:
   - PDF processing happens in real-time
   - Larger PDFs may take longer to process
   - Consider file size limits (default: 4.5MB)

2. **Scalability**:
   - Vercel automatically scales your functions
   - Each request runs independently
   - No database bottlenecks

3. **Cost**:
   - Free tier includes 100GB bandwidth
   - Serverless functions: 100GB-hours free
   - Perfect for moderate traffic

## 🐛 Troubleshooting

### PDF Upload Not Working
- Check file size (should be < 4.5MB)
- Ensure it's a valid PDF file
- Check browser console for errors

### Queries Not Processing
- Ensure PDF was uploaded successfully
- Check if session is still active
- Try refreshing and re-uploading

### Deployment Fails
- Check `requirements.txt` for all dependencies
- Verify Python version compatibility
- Check Vercel build logs

## 📊 Monitoring

View your app's performance in Vercel Dashboard:
- Function logs
- Error tracking
- Usage analytics
- Response times

## 🔒 Security Notes

- PDFs are processed in memory, not stored permanently
- No sensitive data persists between sessions
- CORS enabled for API access
- Environment variables secured in Vercel

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Python on Vercel](https://vercel.com/docs/runtimes/python)
- [Vercel Blob Storage](https://vercel.com/docs/storage/vercel-blob) (optional)

## 🎉 Success!

Your Insurance Query Engine is now live on Vercel! Share the URL with others to test the application.

**Demo URL Format**: `https://bajaj-project.vercel.app`

---

Need help? Check the [Vercel Support](https://vercel.com/support) or raise an issue in your GitHub repository.
