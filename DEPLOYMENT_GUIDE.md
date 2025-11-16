# 🚀 Firebase Deployment Guide

## Your Water Quality Prediction App

### Project Details
- **Project Name:** water-quailty-prediction-raks
- **Project ID:** water-quailty-prediction-raks
- **Firebase Console:** https://console.firebase.google.com/project/water-quailty-prediction-raks

---

## 📋 Prerequisites

1. Install Firebase CLI:
```bash
npm install -g firebase-tools
```

2. Login to Firebase:
```bash
firebase login
```

---

## 🎯 Deployment Steps

### Step 1: Deploy Frontend to Firebase Hosting

```bash
# Initialize Firebase (already done - files created)
# Just deploy:
firebase deploy --only hosting
```

Your app will be live at:
**https://water-quailty-prediction-raks.web.app**

---

### Step 2: Deploy Backend (Python API)

Since Firebase Hosting only serves static files, you need to deploy your Python backend separately. Here are your options:

#### Option A: Deploy to Render (Recommended - Free)

1. Go to https://render.com
2. Sign up/Login
3. Click "New +" → "Web Service"
4. Connect your GitHub repo or upload files
5. Settings:
   - **Name:** water-quality-api
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements_api.txt`
   - **Start Command:** `python api_server.py`
   - **Plan:** Free

6. After deployment, copy your API URL (e.g., `https://water-quality-api.onrender.com`)

7. Update `public/index.html` line 234:
```javascript
const API_URL = 'https://water-quality-api.onrender.com';
```

8. Redeploy frontend:
```bash
firebase deploy --only hosting
```

#### Option B: Deploy to Railway (Free)

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway will auto-detect Python
6. Add environment variables if needed
7. Copy your API URL
8. Update `public/index.html` with the URL
9. Redeploy frontend

#### Option C: Deploy to Google Cloud Run

1. Install Google Cloud SDK
2. Build and deploy:
```bash
gcloud run deploy water-quality-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 📁 Files Created for Deployment

### Frontend (Firebase Hosting)
- ✅ `public/index.html` - Main web app
- ✅ `firebase.json` - Firebase configuration
- ✅ `.firebaserc` - Project settings

### Backend (API Server)
- ✅ `api_server.py` - Python Flask API
- ✅ `requirements_api.txt` - Python dependencies
- ✅ `best_model.h5` - Trained model (11 MB)

---

## 🧪 Testing Locally

### Test Frontend:
```bash
firebase serve
```
Open: http://localhost:5000

### Test Backend:
```bash
source venv/bin/activate
python api_server.py
```
Open: http://localhost:5555

### Test Together:
1. Start backend: `python api_server.py`
2. In another terminal: `firebase serve`
3. Open: http://localhost:5000

---

## 🔧 Configuration

### Update API URL

In `public/index.html`, line 234:
```javascript
// For local testing
const API_URL = 'http://localhost:5555';

// For production (after deploying backend)
const API_URL = 'https://your-backend-url.com';
```

---

## 📊 What Gets Deployed

### Frontend (Firebase Hosting)
- Beautiful web interface
- Drag & drop image upload
- Real-time predictions
- Responsive design
- Firebase Analytics integrated

### Backend (Separate Service)
- Python Flask API
- TensorFlow model inference
- Image processing
- CORS enabled for Firebase domain

---

## 🎉 After Deployment

Your app will be live at:
- **Frontend:** https://water-quailty-prediction-raks.web.app
- **Backend:** https://your-backend-service.com

Users can:
1. Visit your Firebase URL
2. Upload water images
3. Get instant AI predictions
4. See confidence scores

---

## 🐛 Troubleshooting

### Issue: CORS Error
**Solution:** Make sure your backend has CORS enabled for your Firebase domain.

### Issue: Model not loading
**Solution:** Ensure `best_model.h5` is uploaded with your backend deployment.

### Issue: Slow predictions
**Solution:** Backend services on free tier may sleep. First request takes longer.

---

## 💡 Next Steps

1. **Deploy Frontend:**
   ```bash
   firebase deploy
   ```

2. **Deploy Backend:**
   - Choose Render, Railway, or Google Cloud Run
   - Upload your code + model file
   - Copy the API URL

3. **Update Frontend:**
   - Edit `public/index.html` with your API URL
   - Redeploy: `firebase deploy`

4. **Test:**
   - Visit your Firebase URL
   - Upload an image
   - Get predictions!

---

## 📞 Support

- Firebase Console: https://console.firebase.google.com
- Firebase Docs: https://firebase.google.com/docs/hosting
- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app

---

## ✅ Checklist

- [ ] Install Firebase CLI
- [ ] Login to Firebase
- [ ] Deploy frontend: `firebase deploy`
- [ ] Choose backend hosting (Render/Railway/Cloud Run)
- [ ] Deploy backend with model file
- [ ] Update API_URL in index.html
- [ ] Redeploy frontend
- [ ] Test the live app
- [ ] Share your URL! 🎉

Your app URL: **https://water-quailty-prediction-raks.web.app**
