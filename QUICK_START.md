# 🚀 Quick Start - Deploy to Firebase

## ⚡ Fast Deployment (5 minutes)

### Step 1: Install Firebase CLI
```bash
npm install -g firebase-tools
```

### Step 2: Login to Firebase
```bash
firebase login
```

### Step 3: Deploy Frontend
```bash
firebase deploy --only hosting
```

✅ **Your frontend is now live at:**
**https://water-quailty-prediction-raks.web.app**

---

## 🔧 Deploy Backend (Choose One)

### Option A: Render (Easiest - Free)

1. Go to https://render.com and sign up
2. Click "New +" → "Web Service"
3. Connect GitHub or "Deploy from Git URL"
4. Settings:
   - **Name:** water-quality-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements_api.txt`
   - **Start Command:** `gunicorn api_server:app`
   - **Plan:** Free

5. Upload these files:
   - `api_server.py`
   - `requirements_api.txt`
   - `best_model.h5`
   - `Procfile`

6. After deployment, copy your URL (e.g., `https://water-quality-api.onrender.com`)

7. Update `public/index.html` line 234:
```javascript
const API_URL = 'https://water-quality-api.onrender.com';
```

8. Redeploy:
```bash
firebase deploy
```

---

### Option B: Test Locally First

1. **Start Backend:**
```bash
source venv/bin/activate
python api_server.py
```

2. **Test Frontend:**
```bash
firebase serve
```

3. Open http://localhost:5000 in your browser

---

## 📁 Files Ready for Deployment

### Frontend (Firebase Hosting)
- ✅ `public/index.html` - Web app
- ✅ `firebase.json` - Config
- ✅ `.firebaserc` - Project settings

### Backend (Render/Railway)
- ✅ `api_server.py` - Flask API
- ✅ `requirements_api.txt` - Dependencies
- ✅ `best_model.h5` - AI Model
- ✅ `Procfile` - Deployment config
- ✅ `runtime.txt` - Python version

---

## ✅ Deployment Checklist

- [ ] Install Firebase CLI: `npm install -g firebase-tools`
- [ ] Login: `firebase login`
- [ ] Deploy frontend: `firebase deploy`
- [ ] Sign up for Render.com
- [ ] Create new Web Service on Render
- [ ] Upload backend files (api_server.py, requirements_api.txt, best_model.h5)
- [ ] Copy backend URL from Render
- [ ] Update API_URL in public/index.html
- [ ] Redeploy: `firebase deploy`
- [ ] Test your live app! 🎉

---

## 🎯 Your URLs

**Frontend:** https://water-quailty-prediction-raks.web.app
**Backend:** (Your Render URL after deployment)

---

## 💡 Tips

1. **Free Tier Limits:**
   - Render free tier: Service sleeps after 15 min of inactivity
   - First request may take 30-60 seconds to wake up
   - Subsequent requests are fast

2. **Model File:**
   - `best_model.h5` is 11 MB
   - Make sure it's uploaded with your backend

3. **CORS:**
   - Already configured in `api_server.py`
   - Allows requests from your Firebase domain

---

## 🐛 Troubleshooting

**Issue:** "Connection error" in browser
**Fix:** Make sure backend is deployed and API_URL is updated

**Issue:** "Model not found"
**Fix:** Upload `best_model.h5` with your backend files

**Issue:** Slow first request
**Fix:** Normal on free tier - service wakes up from sleep

---

## 🎉 You're Done!

Your Water Quality Prediction app is now live on Firebase!

Share your link: **https://water-quailty-prediction-raks.web.app**
