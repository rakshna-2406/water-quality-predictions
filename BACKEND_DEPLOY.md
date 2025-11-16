# 🚀 Backend Deployment Instructions

## ✅ Frontend Already Deployed!

Your frontend is live at: **https://water-quailty-prediction-raks.web.app**

Now let's deploy the backend...

---

## 📦 Files Needed for Backend Deployment

These files are ready in your project:
- ✅ `api_server.py` - Flask API server
- ✅ `requirements_api.txt` - Python dependencies
- ✅ `best_model.h5` - Your trained model (11 MB)
- ✅ `Procfile` - Deployment configuration
- ✅ `runtime.txt` - Python version

---

## 🎯 Deploy to Render (Free & Easy)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub or Email
3. Verify your email

### Step 2: Create New Web Service
1. Click "New +" button (top right)
2. Select "Web Service"
3. Choose "Build and deploy from a Git repository"
4. Click "Next"

### Step 3: Connect Your Repository

**Option A: If you have GitHub repo:**
- Connect your GitHub account
- Select your repository
- Click "Connect"

**Option B: If no GitHub repo (Manual Upload):**
1. Create a new GitHub repository
2. Upload these files:
   - `api_server.py`
   - `requirements_api.txt`
   - `best_model.h5`
   - `Procfile`
   - `runtime.txt`
3. Connect the repo to Render

### Step 4: Configure Service

Fill in these settings:

**Name:** `water-quality-api`

**Region:** `Oregon (US West)` (or closest to you)

**Branch:** `main` (or your default branch)

**Root Directory:** (leave blank)

**Environment:** `Python 3`

**Build Command:**
```
pip install -r requirements_api.txt
```

**Start Command:**
```
gunicorn api_server:app
```

**Plan:** `Free`

### Step 5: Environment Variables (Optional)
Add if needed:
- `PYTHON_VERSION`: `3.10.13`
- `PORT`: `10000` (Render sets this automatically)

### Step 6: Deploy!
1. Click "Create Web Service"
2. Wait 5-10 minutes for deployment
3. Watch the logs for "Model loaded successfully!"

### Step 7: Copy Your Backend URL
After deployment, you'll see:
```
Your service is live at https://water-quality-api-xxxx.onrender.com
```

Copy this URL!

---

## 🔗 Connect Backend to Frontend

### Step 1: Update Frontend Code

Edit `public/index.html` line 234:

**Change from:**
```javascript
const API_URL = 'http://localhost:5555';
```

**Change to:**
```javascript
const API_URL = 'https://water-quality-api-xxxx.onrender.com';
```
(Replace with your actual Render URL)

### Step 2: Redeploy Frontend

```bash
firebase deploy --only hosting
```

---

## ✅ Test Your Live App!

1. Go to: **https://water-quailty-prediction-raks.web.app**
2. Upload a water image
3. Click "Analyze Water Quality"
4. See the AI prediction!

**Note:** First request may take 30-60 seconds (free tier wakes up from sleep)

---

## 🐛 Troubleshooting

### Issue: "Connection error"
**Solution:** 
- Check if backend is deployed and running
- Verify API_URL in index.html is correct
- Check Render logs for errors

### Issue: "Model not found"
**Solution:**
- Make sure `best_model.h5` is uploaded to Render
- Check file size (should be ~11 MB)

### Issue: CORS error
**Solution:**
- Already configured in `api_server.py`
- Make sure your Firebase domain is in the CORS origins list

### Issue: Slow first request
**Solution:**
- Normal on Render free tier
- Service sleeps after 15 minutes of inactivity
- First request wakes it up (30-60 seconds)
- Subsequent requests are fast

---

## 💡 Alternative: Deploy to Railway

If Render doesn't work, try Railway:

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway auto-detects Python
6. Add environment variables if needed
7. Deploy!
8. Copy your Railway URL
9. Update `public/index.html`
10. Redeploy frontend

---

## 📊 What You'll Have

**Frontend (Firebase):**
- URL: https://water-quailty-prediction-raks.web.app
- Hosting: Firebase (Google)
- Cost: Free
- Features: Static hosting, CDN, SSL

**Backend (Render):**
- URL: https://water-quality-api-xxxx.onrender.com
- Hosting: Render
- Cost: Free (with sleep after 15 min)
- Features: Python, TensorFlow, API

---

## 🎉 Success Checklist

- [x] Frontend deployed to Firebase ✅
- [ ] Backend deployed to Render
- [ ] Backend URL copied
- [ ] Frontend updated with backend URL
- [ ] Frontend redeployed
- [ ] App tested and working

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Firebase Docs: https://firebase.google.com/docs
- Check Render logs for errors
- Verify all files are uploaded

---

## 🚀 Quick Commands

**Deploy Frontend:**
```bash
firebase deploy --only hosting
```

**Test Backend Locally:**
```bash
python3 api_server.py
```

**Check Firebase Status:**
```bash
firebase projects:list
```

---

Your frontend is already live! Just deploy the backend and connect them! 🎉
