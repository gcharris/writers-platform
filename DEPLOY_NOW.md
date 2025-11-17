# Deploy Factory Frontend to Vercel - Quick Start

## 🚀 5-Minute Deployment

### Step 1: Go to Vercel
```
https://vercel.com
```
Click "Sign Up" or "Login" (use GitHub)

### Step 2: Import Project
- Click "Add New..." → "Project"
- Select `gcharris/writers-platform`
- Click "Import"

### Step 3: Configure
**Root Directory:** `factory-frontend` ⚠️ (CRITICAL!)

**Environment Variable:**
```
VITE_API_URL = https://writers-platform-production.up.railway.app/api
```

### Step 4: Deploy
Click "Deploy" → Wait 2 minutes → Done! 🎉

---

## ✅ Verification

After deployment, test:

1. **Homepage:** `https://your-app.vercel.app/`
   - Should show "Writers Factory" with two buttons

2. **Register:** `/register`
   - Create test account: `test@example.com` / `TestPass123!`
   - Should auto-redirect to dashboard

3. **Dashboard:** `/dashboard`
   - Should show "My Projects"
   - Create a test project

4. **Upload:** Click "Upload" on project
   - Drag & drop a text file
   - Should upload successfully

**All working?** ✅ Tell Claude Cloud and they'll start Session 3!

**Issues?** See [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) for troubleshooting

---

## 📊 Expected Results

| Test | Expected Result |
|------|-----------------|
| Homepage | Two buttons: "I Have a Draft" / "Start New Project" |
| Register | Creates account, redirects to dashboard |
| Login | Authenticates, stores JWT token |
| Dashboard | Shows project list, can create projects |
| Upload | Accepts DOCX/PDF/TXT, shows progress |
| Console | No errors, all API calls succeed |

---

## 🆘 Quick Troubleshooting

**Build fails?**
→ Check Root Directory = `factory-frontend`

**Blank page?**
→ Check browser console for errors

**CORS errors?**
→ Already configured ✅ (backend allows `https://*.vercel.app`)

**API calls fail?**
→ Check `VITE_API_URL` environment variable is set

---

## 🎯 What's Already Set Up

✅ Backend deployed to Railway
✅ Backend CORS configured for Vercel
✅ Frontend code complete (Session 2)
✅ Build configuration tested
✅ Documentation complete

**Just need:** Deploy button click!

---

**Time to deploy:** ~5 minutes
**Full guide:** [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)
**Session 2 details:** [SESSION_2_COMPLETE.md](./SESSION_2_COMPLETE.md)
