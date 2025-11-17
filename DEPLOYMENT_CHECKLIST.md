# Railway Deployment Checklist

## ✅ Pre-Deployment (Completed)

- [x] Backend code merged to main branch
- [x] Railway configuration files created (railway.json, Procfile, runtime.txt)
- [x] Environment variables documented (.env.example)
- [x] Deployment guide created (RAILWAY_DEPLOYMENT_GUIDE.md)

## 📋 Deployment Steps (Do These Now)

### 1. Create Railway Project (2 minutes)

- [ ] Go to https://railway.app/new
- [ ] Click "Deploy from GitHub repo"
- [ ] Select `gcharris/writers-platform` repository
- [ ] Railway will begin automatic deployment

### 2. Configure Backend Root Directory (1 minute)

- [ ] In Railway dashboard, click on your new project
- [ ] Go to Settings
- [ ] Under "Build & Deploy" section, set:
  - **Root Directory**: `backend`
  - **Build Command**: (leave empty)
  - **Start Command**: (leave empty - uses railway.json)

### 3. Add PostgreSQL Database (1 minute)

- [ ] In your Railway project, click "+ New" button
- [ ] Select "Database"
- [ ] Choose "PostgreSQL"
- [ ] Wait for database to provision (30 seconds)
- [ ] Verify `DATABASE_URL` appears in Variables tab

### 4. Set Environment Variables (5 minutes)

- [ ] Click "Variables" tab in Railway
- [ ] Click "+ New Variable" for each of these:

**Required - Security:**
```
SECRET_KEY = [Generate with: openssl rand -hex 32]
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
```

**Required - AI Provider Keys:**
```
ANTHROPIC_API_KEY = [Get from https://console.anthropic.com/]
OPENAI_API_KEY = [Get from https://platform.openai.com/api-keys]
GOOGLE_API_KEY = [Get from https://makersuite.google.com/app/apikey]
XAI_API_KEY = [Get from https://console.x.ai/]
```

**Optional - App Config (has defaults):**
```
PROJECT_NAME = Writers Platform API
VERSION = 1.0.0
API_PREFIX = /api
```

### 5. Generate SECRET_KEY

Run this in your terminal:
```bash
openssl rand -hex 32
```

Copy the output and use it as your SECRET_KEY in Railway.

### 6. Deploy (Automatic)

- [ ] After setting variables, Railway will automatically redeploy
- [ ] Watch the deployment logs in Railway dashboard
- [ ] Wait for "Success" status (usually 2-3 minutes)

### 7. Get Your Backend URL

- [ ] Copy your Railway URL (e.g., `https://writers-platform-production.up.railway.app`)
- [ ] Save this - you'll need it for frontend deployment

### 8. Test Deployment (5 minutes)

Run these tests in your terminal (replace URL with your Railway URL):

```bash
# Test 1: Health check
curl https://YOUR-APP.up.railway.app/health

# Test 2: API docs (should return HTML)
curl https://YOUR-APP.up.railway.app/api/docs

# Test 3: Register a user
curl -X POST https://YOUR-APP.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Should return: {"id": "...", "username": "testuser", "email": "test@example.com"}
```

Or open in browser:
- [ ] Visit `https://YOUR-APP.up.railway.app/api/docs` (should show Swagger UI)

## 🎯 Success Criteria

You'll know deployment succeeded when:

- ✅ Railway dashboard shows "Success" status
- ✅ `/health` endpoint returns `{"status": "ok"}`
- ✅ `/api/docs` shows Swagger UI interface
- ✅ User registration works (returns user object with ID)
- ✅ No error messages in Railway logs

## ⚠️ Common Issues

### Issue: "Application failed to respond"

**Fix:**
1. Check Railway logs (Deployments tab)
2. Verify `DATABASE_URL` exists in Variables
3. Verify root directory is set to `backend`

### Issue: "Database connection error"

**Fix:**
1. Verify PostgreSQL addon is created
2. Check `DATABASE_URL` in Variables tab
3. Make sure it starts with `postgresql://`

### Issue: "ModuleNotFoundError"

**Fix:**
1. Check Railway build logs
2. Verify `requirements.txt` exists in backend/
3. Railway should auto-detect and install dependencies

### Issue: AI analysis fails (after deployment works)

**Fix:**
1. Verify all 4 AI API keys are set correctly
2. Test each API key individually
3. Check Railway logs for specific error messages

## 📊 Cost Estimate

**Railway Costs:**
- Starter plan: $5/month
- Includes: 512MB RAM, PostgreSQL database
- Free tier: $5 credit/month (enough for testing)

**AI Provider Costs:**
- Per analysis (5 agents): $0.50 - $2.00
- Budget accordingly based on expected usage

## 🎉 Next Steps (After Successful Deployment)

1. **Save Your Backend URL** - You'll need it for Session 2
2. **Test All Endpoints** - Use the Swagger UI at `/api/docs`
3. **Session 2: Deploy Factory Frontend**
   - Build React app for Writers Factory
   - Connect to this backend
   - Deploy to Vercel
4. **Session 3: Update Community Frontend**
   - Add badge system
   - Integrate with Factory
   - Redeploy to Vercel

## 📚 Resources

- **Full Deployment Guide**: See [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)
- **Backend API Docs**: See [backend/README.md](./backend/README.md)
- **Railway Docs**: https://docs.railway.app
- **Need Help?** Open an issue: https://github.com/gcharris/writers-platform/issues

---

**Estimated Total Time: 15-20 minutes**

Good luck! 🚀
