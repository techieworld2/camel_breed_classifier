# 🚀 Deployment Guide - Camel Classifier

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐
│  Vercel         │ ──────► │  Railway/Render  │
│  (React App)    │  API    │  (FastAPI + ML)  │
└─────────────────┘         └──────────────────┘
```

- **Frontend (React)** → Vercel (Free, Fast CDN)
- **Backend (FastAPI + PyTorch)** → Railway or Render (ML-friendly)

---

## 📦 Part 1: Deploy Backend (FastAPI) on Railway

### Why Railway?
- ✅ Free tier with 500 hours/month
- ✅ Supports large files (ML models)
- ✅ PostgreSQL database included
- ✅ Easy environment variables

### Steps:

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your repository

3. **Configure Backend Service**
   ```
   Root Directory: fastapi_backend/
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Set Environment Variables** (in Railway dashboard)
   ```
   SECRET_KEY=<generate with: openssl rand -hex 32>
   GEMINI_API_KEY=<your-gemini-api-key>
   FRONTEND_URL=https://your-app.vercel.app
   ```

5. **Deploy**
   - Railway will auto-deploy
   - Get your backend URL: `https://your-app.railway.app`
   - Test at: `https://your-app.railway.app/docs`

---

## 🎨 Part 2: Deploy Frontend (React) on Vercel

### Steps:

1. **Create Vercel Account**
   - Go to https://vercel.com
   - Sign up with GitHub

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Select `frontend` as Root Directory

3. **Configure Build Settings**
   ```
   Framework Preset: Create React App
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: build
   Install Command: npm install
   ```

4. **Set Environment Variables** (in Vercel dashboard)
   ```
   REACT_APP_API_URL=https://your-backend.railway.app/api
   ```

5. **Deploy**
   - Click "Deploy"
   - Your app will be live at: `https://your-app.vercel.app`

---

## 🔄 Alternative: Deploy Backend on Render

If you prefer Render over Railway:

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your repository
   - Select `fastapi_backend` folder

3. **Configure Service**
   ```
   Name: camel-classifier-api
   Environment: Python 3
   Region: Choose closest to you
   Branch: main
   Root Directory: fastapi_backend
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Set Environment Variables**
   - Same as Railway (SECRET_KEY, GEMINI_API_KEY, FRONTEND_URL)

5. **Choose Plan**
   - Free tier: $0/month (sleeps after 15 min inactivity)
   - Starter: $7/month (always on, 512MB RAM)

---

## 📋 Pre-Deployment Checklist

### Backend Files Created ✅
- [x] `Procfile` - For Heroku/Render
- [x] `runtime.txt` - Python version
- [x] `railway.toml` - Railway config
- [x] Updated `main.py` - Dynamic PORT & CORS

### Frontend Files Created ✅
- [x] `vercel.json` - Vercel routing config
- [x] `.env.production` - Production API URL
- [x] Updated `api.js` - Uses REACT_APP_API_URL

### Before Deploying:

**Backend:**
- [ ] Ensure `best_model.pt` is in Git (< 100MB)
  - If > 100MB, use Git LFS: `git lfs track "*.pt"`
- [ ] Test locally: `cd fastapi_backend && python main.py`
- [ ] Verify `/docs` endpoint works

**Frontend:**
- [ ] Update `.env.production` with real backend URL
- [ ] Test build locally: `cd frontend && npm run build`
- [ ] Test production build: `serve -s build`

---

## 🔐 Environment Variables Reference

### Backend (Railway/Render)
```env
SECRET_KEY=<openssl rand -hex 32>
GEMINI_API_KEY=AIzaSy...
FRONTEND_URL=https://your-app.vercel.app
PORT=8000  # Auto-set by platform
```

### Frontend (Vercel)
```env
REACT_APP_API_URL=https://your-backend.railway.app/api
```

---

## 🧪 Testing Deployed App

1. **Backend Health Check**
   ```bash
   curl https://your-backend.railway.app/health
   # Should return: {"status":"healthy"}
   ```

2. **Backend API Docs**
   - Visit: `https://your-backend.railway.app/docs`
   - Test signup/login directly in Swagger UI

3. **Frontend**
   - Visit: `https://your-app.vercel.app`
   - Try signup → login → classify image

---

## 📊 Model File Size Warning

Your `best_model.pt` file size matters:

- **< 25MB**: ✅ No issues, push to Git normally
- **25-100MB**: ⚠️ Use Git LFS
  ```bash
  git lfs install
  git lfs track "*.pt"
  git add .gitattributes
  git add fastapi_backend/best_model.pt
  git commit -m "Add model with LFS"
  ```
- **> 100MB**: 🚨 Use cloud storage
  - Upload to Google Drive/S3
  - Download on Railway startup
  - Or use Railway Volumes

---

## 🆓 Cost Breakdown

### Free Tier Options:
```
Frontend (Vercel):
- ✅ FREE unlimited
- Bandwidth: 100GB/month
- Builds: Unlimited

Backend Option 1 (Railway):
- ✅ FREE 500 hours/month (~20 days)
- 512MB RAM, 1GB disk
- Sleeps after 30min inactivity

Backend Option 2 (Render):
- ✅ FREE with limitations
- Sleeps after 15min inactivity
- 512MB RAM
```

### Paid Options (if you need always-on):
```
Railway Starter: $5/month
- 8GB RAM, 100GB disk
- No sleep, custom domain

Render Starter: $7/month
- 512MB RAM
- No sleep, SSL included
```

---

## 🐛 Common Issues

### Issue 1: CORS Error on Frontend
**Fix:** Update `FRONTEND_URL` in backend env vars to match your Vercel URL

### Issue 2: Model Not Found
**Fix:** Ensure `best_model.pt` is in `fastapi_backend/` and committed to Git

### Issue 3: Gemini API Not Working
**Fix:** Verify `GEMINI_API_KEY` is set in Railway/Render dashboard

### Issue 4: Backend Build Fails (Torch)
**Fix:** Ensure `requirements.txt` has correct PyTorch CPU version:
```
torch==2.4.1+cpu
torchvision==0.19.1+cpu
--extra-index-url https://download.pytorch.org/whl/cpu
```

### Issue 5: Database Resets on Restart
**Fix:** 
- Railway: Use Railway Volumes for persistent storage
- Render: Use Render Disks
- Or migrate to PostgreSQL

---

## 🚀 Quick Deploy Commands

### Push to GitHub (if not already)
```bash
cd "/home/anas/Pictures/combined images/Camel_FPY"
git init
git add .
git commit -m "Initial commit - Camel Classifier"
git branch -M main
git remote add origin https://github.com/yourusername/camel-classifier.git
git push -u origin main
```

### Connect to Railway
```bash
# Install Railway CLI (optional)
npm install -g @railway/cli
railway login
railway link
railway up
```

### Connect to Vercel
```bash
# Install Vercel CLI (optional)
npm install -g vercel
cd frontend
vercel login
vercel
```

---

## 🎯 Post-Deployment

1. **Update README.md** with live URLs
2. **Test all features**: Signup, Login, Classify, Facts
3. **Monitor logs** in Railway/Render dashboard
4. **Set up custom domain** (optional)
5. **Enable analytics** in Vercel dashboard

---

## 📚 Resources

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

---

Your app is ready to deploy! 🐪✨

**Recommended Flow:**
1. Deploy backend to Railway first
2. Copy backend URL
3. Deploy frontend to Vercel with backend URL
4. Test end-to-end
