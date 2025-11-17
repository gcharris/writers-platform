# Vercel Deployment Guide - Factory Frontend

## Quick Start

Deploy the Factory frontend to Vercel in 5 minutes!

**What you need:**
- Vercel account (free tier works)
- GitHub repository access
- Railway backend URL: `https://writers-platform-production.up.railway.app/api`

---

## Step-by-Step Deployment

### Step 1: Go to Vercel

1. Navigate to **https://vercel.com**
2. Click **"Sign Up"** or **"Login"**
3. Connect with GitHub (recommended)

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Find and select **`gcharris/writers-platform`** repository
3. Click **"Import"**

### Step 3: Configure Project

**IMPORTANT:** Set the root directory!

**Root Directory:**
```
factory-frontend
```

**Framework Preset:** Vite (should auto-detect)

**Build & Development Settings:**
```
Build Command:        npm run build
Output Directory:     dist
Install Command:      npm install
Development Command:  npm run dev
```

### Step 4: Add Environment Variable

Click **"Environment Variables"** section:

**Variable Name:**
```
VITE_API_URL
```

**Value:**
```
https://writers-platform-production.up.railway.app/api
```

Click **"Add"**

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait ~2 minutes for build to complete
3. You'll see a success message with your deployment URL

---

## Expected Build Output

Your Vercel build should look like this:

```
Running build command: npm run build

> writers-factory@0.0.0 build
> tsc -b && vite build

vite v6.0.7 building for production...
✓ 1234 modules transformed.
dist/index.html                   0.46 kB │ gzip:  0.30 kB
dist/assets/react-DhAJQ8wH.svg    4.13 kB │ gzip:  2.05 kB
dist/assets/index-BVJKVjJV.css   24.32 kB │ gzip:  6.84 kB
dist/assets/index-DQqq0m5N.js   393.24 kB │ gzip: 124.37 kB

✓ built in 4.82s

Build Completed in /vercel/output [2m 15s]
```

---

## After Deployment

### Get Your Vercel URL

After deployment, you'll receive a URL like:
```
https://writers-platform-<random>.vercel.app
```

**Good news!** CORS is already configured ✅

The backend already allows all Vercel deployments:
```python
allow_origins=[
    "https://*.vercel.app"  # All Vercel deployments allowed
]
```

### Test the Deployment

Open the Vercel URL in your browser:

**Expected:**
1. You see the Factory homepage
2. "I Have a Draft" and "Start New Project" buttons visible
3. Navigation menu works

**Test these pages:**
- `/` - Home page ✓
- `/login` - Login page ✓
- `/register` - Register page ✓

---

## Verification Checklist

After deployment, verify everything works:

### 1. Test Homepage
```
https://your-app.vercel.app/
```

**Expected:**
- ✅ Page loads without errors
- ✅ "Writers Factory" branding visible
- ✅ Two main buttons: "I Have a Draft" and "Start New Project"
- ✅ Navigation menu at top

### 2. Test Authentication Pages

**Login Page:**
```
https://your-app.vercel.app/login
```

**Expected:**
- ✅ Email and password fields
- ✅ "Login" button
- ✅ Link to register page

**Register Page:**
```
https://your-app.vercel.app/register
```

**Expected:**
- ✅ Email, password, confirm password fields
- ✅ "Register" button
- ✅ Link to login page

### 3. Test Registration Flow

1. Go to `/register`
2. Enter email: `test@example.com`
3. Enter password: `TestPass123!`
4. Confirm password
5. Click "Register"

**Expected:**
- ✅ Registration succeeds
- ✅ Auto-redirect to dashboard
- ✅ Dashboard shows "My Projects"

### 4. Test Project Creation

1. After login, you should be on `/dashboard`
2. Click "Create New Project"
3. Enter project name: "Test Project"
4. Click "Create"

**Expected:**
- ✅ Project created successfully
- ✅ Project appears in list
- ✅ Can navigate to upload page

### 5. Test File Upload

1. From dashboard, click "Upload" on a project
2. Drag and drop a `.txt` file (create a test file)
3. Click "Upload"

**Expected:**
- ✅ File upload progress shows
- ✅ Upload completes
- ✅ Redirects to editor page

### 6. Check Browser Console

Open browser DevTools (F12) → Console tab

**Expected:**
- ✅ No JavaScript errors
- ✅ No CORS errors
- ✅ API calls succeed (200 or 201 status)

---

## Troubleshooting

### Issue 1: Build Fails

**Error:**
```
npm ERR! code ENOENT
npm ERR! syscall open
npm ERR! path /vercel/path0/package.json
```

**Fix:**
- Make sure **Root Directory** is set to `factory-frontend`
- Not `backend` or `/` (root)

### Issue 2: Page Shows Blank White Screen

**Cause:** Usually a build or routing issue

**Fix:**
1. Check browser console for errors
2. Verify `vercel.json` exists in `factory-frontend/`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### Issue 3: API Calls Failing (CORS)

**Error in browser console:**
```
Access to fetch at 'https://...' from origin 'https://your-app.vercel.app'
has been blocked by CORS policy
```

**This shouldn't happen** (already configured), but if it does:

**Check:**
1. Is `VITE_API_URL` environment variable set correctly?
2. Open DevTools → Network tab → Check API request URL
3. Should be: `https://writers-platform-production.up.railway.app/api/...`

### Issue 4: Environment Variable Not Working

**Symptom:** API calls go to wrong URL or `undefined`

**Fix:**
1. Go to Vercel dashboard → Project → Settings → Environment Variables
2. Make sure `VITE_API_URL` is set
3. **Important:** Redeploy after adding/changing environment variables
   - Go to Deployments tab
   - Click "Redeploy" on latest deployment

### Issue 5: 404 Errors on Refresh

**Symptom:** Navigating to `/login` works, but refreshing the page shows 404

**Fix:** Make sure `vercel.json` has rewrites configuration (see Issue 2)

---

## Performance Verification

### Check Build Size

After deployment, check that build is optimized:

**Expected sizes:**
- Total bundle: ~400KB uncompressed
- Gzipped: ~125KB
- Initial load: < 500ms

### Check Lighthouse Score

1. Open Chrome DevTools
2. Go to "Lighthouse" tab
3. Run audit

**Target scores:**
- Performance: 90+
- Accessibility: 90+
- Best Practices: 90+
- SEO: 90+

---

## Custom Domain (Optional)

### Add Custom Domain

If you want to use `writersfactory.app`:

1. Go to Vercel dashboard → Project → Settings → Domains
2. Click "Add Domain"
3. Enter: `writersfactory.app`
4. Follow Vercel's DNS instructions
5. Update your domain registrar's DNS:
   - Add `A` record or `CNAME` as instructed by Vercel

### Update Backend CORS for Custom Domain

The backend already has:
```python
"https://writersfactory.app",
"https://www.writersfactory.app",
```

So custom domain should work immediately! ✅

---

## Production Checklist

Before announcing to users:

- [ ] Deployment successful on Vercel
- [ ] Homepage loads correctly
- [ ] Registration flow works
- [ ] Login flow works
- [ ] Dashboard shows projects
- [ ] File upload works
- [ ] Editor displays scenes
- [ ] Analysis workflow works
- [ ] No console errors
- [ ] No CORS errors
- [ ] API calls succeed
- [ ] Mobile responsive (test on phone)
- [ ] Lighthouse score 90+
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active (Vercel auto)

---

## Monitoring

### Vercel Analytics (Free)

Enable built-in analytics:

1. Go to Vercel dashboard → Project → Analytics
2. Click "Enable"
3. View page views, performance, errors

### Error Tracking

For production, consider adding:
- **Sentry** (error tracking)
- **LogRocket** (session replay)
- **Hotjar** (user behavior)

---

## Deployment Workflow

### Automatic Deployments

Vercel automatically deploys when you push to GitHub:

**Main branch:**
- Push to `main` → Production deployment
- URL: `https://your-app.vercel.app`

**Other branches:**
- Push to any branch → Preview deployment
- URL: `https://your-app-<branch>-<hash>.vercel.app`

### Manual Deployment

Trigger manual deployment:

1. Go to Vercel dashboard → Deployments
2. Click "..." menu on a deployment
3. Click "Redeploy"

---

## Next Steps After Deployment

### 1. Share the URL

Send the Vercel URL to:
- Claude Cloud (for Session 3 testing)
- Beta testers
- Team members

### 2. Test All Features

Go through complete user journey:
- Register → Login → Create Project → Upload File → Edit Scene → Run Analysis

### 3. Report Issues

If you find any issues:
- Check browser console for errors
- Check Vercel deployment logs
- Check Railway backend logs
- Document the issue

### 4. Prepare for Session 3

Once Factory frontend is verified working:
- Claude Cloud can start Session 3 (Community frontend)
- Integration testing will use both frontends
- Final polish and optimization

---

## Quick Commands

```bash
# Check deployment status
vercel --prod

# View deployment logs
vercel logs <deployment-url>

# List all deployments
vercel ls

# Rollback to previous deployment
vercel rollback
```

---

## Success Criteria

✅ **Deployment is successful when:**

1. Build completes without errors
2. Homepage loads at Vercel URL
3. All pages accessible (/, /login, /register, /dashboard, /upload, /editor, /analysis)
4. Registration creates new user
5. Login authenticates and redirects to dashboard
6. File upload works
7. API calls succeed (check Network tab)
8. No CORS errors
9. No console errors
10. Mobile responsive

---

## Support

If you encounter issues:

1. **Check Vercel logs:** Dashboard → Deployments → Click deployment → Logs
2. **Check Railway backend:** Make sure backend is running
3. **Check CORS:** Verify `https://*.vercel.app` is in allow_origins
4. **Check environment variables:** VITE_API_URL must be set
5. **Review:** [SESSION_2_COMPLETE.md](./SESSION_2_COMPLETE.md) for frontend details

---

**Status:** Ready to deploy! 🚀

**Estimated time:** 5 minutes

**Next:** Click "Deploy" button on Vercel!
