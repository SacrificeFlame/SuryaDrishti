# Railway Custom Build Command

## For Frontend Service

### If Using Docker (Current):
**Build Command:** (leave empty - Dockerfile handles it)

**Start Command:** 
```
npm start
```

### If Using Nixpacks (Recommended):
**Build Command:**
```
npm ci && npm run build
```

**Start Command:**
```
npm start
```

---

## For Backend Service

### If Using Docker:
**Build Command:** (leave empty - Dockerfile handles it)

**Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### If Using Nixpacks:
**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Recommended Settings for Frontend

**Root Directory:** `frontend`

**Build Command:**
```
npm ci && npm run build
```

**Start Command:**
```
npm start
```

**Environment Variables:**
- `NEXT_PUBLIC_API_URL` = `https://your-backend-url.railway.app/api/v1`

---

## Recommended Settings for Backend

**Root Directory:** `backend`

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
- `DATABASE_URL` = (auto-set by PostgreSQL)
- `TWILIO_ACCOUNT_SID` = your_sid
- `TWILIO_AUTH_TOKEN` = your_token
- `TWILIO_FROM_NUMBER` = +1234567890
- `CORS_ORIGINS` = https://your-frontend-url.railway.app

---

## Quick Copy-Paste

### Frontend Build Command:
```bash
npm ci && npm run build
```

### Frontend Start Command:
```bash
npm start
```

### Backend Build Command:
```bash
pip install -r requirements.txt
```

### Backend Start Command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

