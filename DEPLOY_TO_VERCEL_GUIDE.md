# 🚀 Complete Guide to Deploy on Vercel - Step by Step

## 📋 Prerequisites Checklist

Before starting, make sure you have:
- ✅ A computer with internet connection
- ✅ Your project files ready (which you already have!)
- ✅ About 10-15 minutes of time

---

## 🎯 Step 1: Create a Vercel Account (Free)

1. **Open your browser** and go to: https://vercel.com/signup

2. **Choose signup method**:
   - Click **"Continue with GitHub"** (Recommended)
   - OR **"Continue with GitLab"**
   - OR **"Continue with Email"**

3. **Complete signup**:
   - If using GitHub: Authorize Vercel
   - If using Email: Verify your email address

4. **Skip the onboarding** (you can do it later)

---

## 🔧 Step 2: Install Required Tools

### Option A: Using NPM (Recommended)

1. **Open PowerShell** or Command Prompt

2. **Install Node.js** if you don't have it:
   - Download from: https://nodejs.org/
   - Choose "LTS" version
   - Run installer with default settings

3. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

4. **Verify installation**:
   ```bash
   vercel --version
   ```
   You should see a version number like `32.0.0`

### Option B: Direct Download
- Download Vercel Desktop from: https://vercel.com/desktop

---

## 📁 Step 3: Prepare Your Project

1. **Open PowerShell** in your project folder:
   ```bash
   cd C:\Users\rupga\OneDrive\Desktop\8\Bajaj_Project
   ```

2. **Check your files** are ready:
   ```bash
   ls
   ```
   You should see:
   - ✅ `api/` folder
   - ✅ `vercel.json`
   - ✅ `requirements.txt`
   - ✅ `index.html`

3. **Update your .env file** (Optional but recommended):
   - Open `.env` file in Notepad
   - Replace `your_gemini_api_key_here` with actual key if you have one
   - Save the file

---

## 🌐 Step 4: Deploy to Vercel

### Method 1: Using Vercel CLI (Easiest)

1. **Login to Vercel**:
   ```bash
   vercel login
   ```
   - Enter your email
   - Check your email for verification
   - Click the verification link

2. **Start deployment**:
   ```bash
   vercel
   ```

3. **Answer the prompts**:
   ```
   ? Set up and deploy "Bajaj_Project"? [Y/n] → Y
   ? Which scope do you want to deploy to? → Your Username
   ? Link to existing project? [y/N] → N
   ? What's your project's name? → bajaj-insurance-engine
   ? In which directory is your code located? → ./ (just press Enter)
   ? Want to modify these settings? [y/N] → N
   ```

4. **Wait for deployment** (2-3 minutes)
   - You'll see progress messages
   - When done, you'll get a URL like: `https://bajaj-insurance-engine.vercel.app`

5. **Deploy to production**:
   ```bash
   vercel --prod
   ```

### Method 2: Using Git + Vercel Dashboard

1. **Initialize Git** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub repository**:
   - Go to: https://github.com/new
   - Name: `bajaj-insurance-engine`
   - Make it Public
   - Click "Create repository"

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/bajaj-insurance-engine.git
   git branch -M main
   git push -u origin main
   ```

4. **Import to Vercel**:
   - Go to: https://vercel.com/new
   - Click "Import Git Repository"
   - Select your repository
   - Click "Import"
   - Click "Deploy"

---

## ⚙️ Step 5: Configure Environment Variables (Optional)

1. **Go to your Vercel Dashboard**: https://vercel.com/dashboard

2. **Click on your project**: `bajaj-insurance-engine`

3. **Go to Settings** → **Environment Variables**

4. **Add variables** (if you have API keys):
   - Click "Add"
   - Key: `GOOGLE_API_KEY`
   - Value: `your-actual-api-key`
   - Environment: Select all (Production, Preview, Development)
   - Click "Save"

5. **Add Blob Storage** (Optional, for persistent PDF storage):
   - Go to **Storage** tab
   - Click "Create Database"
   - Choose "Blob"
   - Follow setup instructions

6. **Redeploy** to apply changes:
   ```bash
   vercel --prod
   ```

---

## ✅ Step 6: Test Your Deployed App

1. **Open your deployed URL**:
   - Example: `https://bajaj-insurance-engine.vercel.app`

2. **Test features**:
   - ✅ Check if page loads
   - ✅ Try sample queries (without PDF)
   - ✅ Upload a PDF and test
   - ✅ Submit queries and check results

3. **Check API health**:
   - Visit: `https://your-app.vercel.app/health`
   - Should show "healthy" status

---

## 🔍 Step 7: Monitor & Manage

### View Logs
1. Go to Vercel Dashboard
2. Click your project
3. Go to "Functions" tab
4. Click on any function to see logs

### View Analytics
1. In project dashboard
2. Click "Analytics" tab
3. See visitor stats and performance

### Update Your App
1. Make changes locally
2. Deploy again:
   ```bash
   vercel --prod
   ```

---

## 🎨 Step 8: Custom Domain (Optional)

### Use Vercel Subdomain
Your app already has: `https://bajaj-insurance-engine.vercel.app`

### Add Custom Domain
1. Buy domain from: Namecheap, GoDaddy, or Google Domains
2. In Vercel Dashboard → Settings → Domains
3. Add your domain
4. Follow DNS configuration steps

---

## 📊 What's Included in Free Tier

Vercel's free tier includes:
- ✅ **100 GB** Bandwidth
- ✅ **100 GB-Hours** Serverless Functions
- ✅ **Unlimited** deployments
- ✅ **HTTPS** included
- ✅ **Auto-scaling**
- ✅ **Global CDN**

Perfect for your project! 🎉

---

## 🐛 Troubleshooting Common Issues

### Issue 1: "Command not found: vercel"
**Solution**:
```bash
npm install -g vercel
```

### Issue 2: "Build failed"
**Solution**:
- Check `requirements.txt` has all packages
- Ensure `vercel.json` is properly formatted
- Check Python version compatibility

### Issue 3: "Module not found"
**Solution**:
- Make sure all imports are in `requirements.txt`
- Redeploy: `vercel --prod --force`

### Issue 4: "PDF upload not working"
**Solution**:
- File size limit is 4.5MB
- Ensure PDF processing libraries are in requirements.txt

### Issue 5: "CORS error"
**Solution**:
- Already handled in your code!
- If still issues, check browser console

---

## 🎯 Quick Deployment Commands

```bash
# First time setup
npm install -g vercel
vercel login
vercel

# Deploy to production
vercel --prod

# Force redeploy
vercel --prod --force

# Check deployment status
vercel ls

# View logs
vercel logs

# Remove deployment
vercel remove bajaj-insurance-engine
```

---

## 📱 Share Your App

Once deployed, share your app URL:

**Your App URL**: `https://bajaj-insurance-engine.vercel.app`

Share with:
- Friends and colleagues for testing
- On your resume/portfolio
- In project documentation

---

## 🎉 Congratulations!

Your Insurance Query Engine is now LIVE on the internet! 

### What You've Achieved:
- ✅ Deployed a Python Flask API
- ✅ Serverless architecture
- ✅ Global CDN distribution
- ✅ Automatic HTTPS
- ✅ PDF processing capability
- ✅ No database required
- ✅ Free hosting

### Next Steps:
1. Test all features thoroughly
2. Share with others for feedback
3. Add to your portfolio
4. Consider adding more features

---

## 📞 Need Help?

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel Support**: https://vercel.com/support
- **Community Forum**: https://github.com/vercel/vercel/discussions
- **Status Page**: https://www.vercel-status.com/

---

## 📝 Deployment Checklist

Before deploying, ensure:
- [ ] All files are saved
- [ ] `.env` file exists (even if empty)
- [ ] `vercel.json` is configured
- [ ] `requirements.txt` has all dependencies
- [ ] API works locally
- [ ] Frontend connects to API

After deploying:
- [ ] Test health endpoint
- [ ] Test query without PDF
- [ ] Test PDF upload
- [ ] Test query with PDF
- [ ] Check logs for errors
- [ ] Share URL for testing

---

## 🚀 Final Command Summary

```bash
# Complete deployment in 3 commands:
npm install -g vercel
vercel login
vercel --prod
```

That's it! Your app is live! 🎊

---

**Deployed URL Format**: `https://[project-name].vercel.app`
**API Endpoints**:
- Health: `https://[project-name].vercel.app/health`
- Query: `https://[project-name].vercel.app/query`
- Upload: `https://[project-name].vercel.app/upload`

---

💡 **Pro Tip**: Save your deployment URL in a text file for easy access!
