# Render Deployment Guide for ChemViz

## Backend Deployment on Render

### 1. Create Web Service
- Go to [Render Dashboard](https://dashboard.render.com/)
- Click **New +** → **Web Service**
- Connect your GitHub repository: `ishansurdi/ChemViz`
- Configure:

**Basic Settings:**
- Name: `chemviz-backend`
- Root Directory: `backend`
- Environment: `Python 3`
- Build Command: `./build.sh`
- Start Command: `gunicorn chemviz.wsgi:application`

**Environment Variables (Add these in Render):**
```
SECRET_KEY=your-super-secret-key-change-this-in-production-xyz123
DEBUG=False
DATABASE_NAME=chemviz_prod.db
ALLOWED_HOSTS=chemviz-backend.onrender.com
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
MAX_DATASET_HISTORY=5
RENDER=True
```

### 2. Frontend Deployment on Render

**Option A: Static Site (Recommended)**
- Click **New +** → **Static Site**
- Connect repository: `ishansurdi/ChemViz`
- Configure:

**Basic Settings:**
- Name: `chemviz-frontend`
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`

**Environment Variable:**
```
VITE_API_BASE_URL=https://chemviz-backend.onrender.com/api
```

**Option B: Web Service (if you need server)**
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Start Command: `npm run preview -- --host 0.0.0.0 --port $PORT`

---

## Local Development Setup

### Backend (No changes needed)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```
Runs on: http://127.0.0.1:8000

### Frontend (Update .env for local)
Create `frontend/.env`:
```
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

```powershell
cd frontend
npm run dev
```
Runs on: http://localhost:3000

### Desktop (No changes needed)
```powershell
cd desktop
.\venv\Scripts\Activate.ps1
python main.py
```

---

## After Deployment

1. **Get your backend URL**: `https://chemviz-backend.onrender.com`
2. **Update frontend .env** (if deploying frontend separately)
3. **Test endpoints**:
   - Backend: `https://chemviz-backend.onrender.com/`
   - API Health: `https://chemviz-backend.onrender.com/api/health/`
   - Frontend: `https://chemviz-frontend.onrender.com`

4. **Create superuser on Render** (via Shell):
```bash
python manage.py createsuperuser
```

---

## Important Notes

✅ **Free Tier**: Render free tier spins down after 15 min inactivity (first request takes ~30s)
✅ **Database**: Using SQLite (persists on Render disk, but use PostgreSQL for production)
✅ **CORS**: Already configured to accept all origins in development
✅ **Static Files**: WhiteNoise handles static files automatically
✅ **Local & Production**: Everything works on both without code changes!

---

## Troubleshooting

**Build fails?**
- Check `build.sh` has execute permissions: `chmod +x build.sh`
- Verify all dependencies in `requirements.txt`

**CORS errors?**
- Add your frontend URL to `CORS_ALLOWED_ORIGINS` in settings.py if restricting origins

**Static files not loading?**
- Run: `python manage.py collectstatic --no-input`
- Check `STATIC_ROOT` path in settings

**Database errors?**
- Render will create new DB on first deploy
- Run migrations manually: `python manage.py migrate`
