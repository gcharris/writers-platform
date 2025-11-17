# Factory Frontend Testing Checklist

## Your Vercel URL

First, get your deployment URL from Vercel:
- It will look like: `https://writers-platform-xxxxx.vercel.app`
- Or check Vercel dashboard → Your project → "Visit" button

---

## 🧪 Testing Steps

### 1. Homepage Test ✅

**Open:** `https://your-app.vercel.app/`

**Expected to see:**
- ✅ "Writers Factory" heading/branding
- ✅ Two main buttons:
  - "I Have a Draft" (left side)
  - "Start New Project" (right side)
- ✅ Navigation menu at top with "Login" link
- ✅ Clean, professional design

**If this works, continue! If not, check browser console (F12) for errors.**

---

### 2. Registration Test ✅

**Navigate to:** `/register`

**Steps:**
1. Enter email: `test@example.com`
2. Enter password: `TestPass123!`
3. Confirm password: `TestPass123!`
4. Click "Register"

**Expected:**
- ✅ Registration succeeds
- ✅ Automatically redirects to `/dashboard`
- ✅ You see "My Projects" heading
- ✅ "Create New Project" button visible

**If registration fails:**
- Check browser console (F12) for errors
- Common issue: Backend API not responding (check Railway is running)

---

### 3. Dashboard Test ✅

**You should be at:** `/dashboard` (after registration)

**Expected to see:**
- ✅ "My Projects" heading
- ✅ "Create New Project" button
- ✅ Empty state message (if no projects yet)
- ✅ Navigation shows your email or "Logout" option

**Test Create Project:**
1. Click "Create New Project"
2. Enter name: "Test Novel"
3. Click "Create"

**Expected:**
- ✅ Modal/form closes
- ✅ "Test Novel" appears in project list
- ✅ Project has "Upload" and "Delete" buttons

---

### 4. Logout/Login Test ✅

**Test Logout:**
1. Click "Logout" in navigation
2. Should redirect to `/login`

**Test Login:**
1. Enter email: `test@example.com`
2. Enter password: `TestPass123!`
3. Click "Login"

**Expected:**
- ✅ Login succeeds
- ✅ Redirects to `/dashboard`
- ✅ Your "Test Novel" project still there

---

### 5. Upload Test ✅

**Create a test file first:**
```bash
echo "Chapter 1: The Beginning\n\nIt was a dark and stormy night..." > test-manuscript.txt
```

**Steps:**
1. On dashboard, click "Upload" button on your "Test Novel" project
2. Should navigate to `/upload?projectId=...`
3. Drag and drop `test-manuscript.txt` onto the upload area
   - Or click "Choose File" and select it
4. Click "Upload" button

**Expected:**
- ✅ File upload progress shows
- ✅ Upload completes
- ✅ Redirects to `/editor/:id`
- ✅ You see scene list on left side

---

### 6. Editor Test ✅

**You should be at:** `/editor/:id` (after upload)

**Expected to see:**
- ✅ Scene list on left (should show "Chapter 1: The Beginning")
- ✅ Click on a scene to view content
- ✅ Scene content displays on right side
- ✅ "Edit" button available

**Test Edit:**
1. Click "Edit" on a scene
2. Change some text
3. Click "Save"

**Expected:**
- ✅ Save succeeds
- ✅ Changes persist

---

### 7. Analysis Test ✅

**Navigate to:** `/analysis`

**Expected to see:**
- ✅ "AI Analysis" heading
- ✅ Dropdown to select a project
- ✅ Model selection (Claude, GPT-4, Gemini)
- ✅ Analysis type selection (character, plot, voice, etc.)
- ✅ "Run Analysis" button

**Test (if you have API keys configured):**
1. Select your "Test Novel" project
2. Select a model (e.g., "Claude Sonnet")
3. Select analysis type (e.g., "Character Analysis")
4. Click "Run Analysis"

**Expected:**
- ✅ Analysis starts
- ✅ Progress shows (0% → 100%)
- ✅ When complete, results display
- ✅ Results show scoring and feedback

**Note:** Analysis requires backend API keys. If not configured, you'll see an error (that's expected).

---

## 🔍 Browser Console Check

**Open DevTools (F12) → Console tab**

**Should NOT see:**
- ❌ CORS errors
- ❌ 404 errors for API calls
- ❌ JavaScript errors
- ❌ Failed to fetch errors

**Should see:**
- ✅ Successful API calls (200, 201 status codes)
- ✅ Maybe some logs from the app
- ✅ No red error messages

**Check Network tab:**
- ✅ API calls go to: `https://writers-platform-production.up.railway.app/api/...`
- ✅ Responses come back with data
- ✅ Authorization headers present (after login)

---

## 📱 Mobile Test (Optional)

**Open on phone or resize browser:**
1. Homepage should be responsive
2. Navigation should work
3. Forms should be usable
4. Buttons should be tappable

---

## ✅ Success Criteria

**Deployment is successful when:**

- [x] Homepage loads and looks good
- [x] Registration creates a new user
- [x] Login authenticates and redirects to dashboard
- [x] Dashboard shows projects
- [x] Can create new project
- [x] Can upload a file
- [x] Editor shows scenes
- [x] Analysis page loads
- [x] No console errors
- [x] No CORS errors
- [x] API calls succeed

---

## 🐛 Common Issues & Fixes

### Issue 1: "Network Error" or "Failed to fetch"

**Cause:** Backend API not running or CORS issue

**Check:**
```bash
curl https://writers-platform-production.up.railway.app/health
```

**Should return:** `{"status":"healthy"}`

**Fix:** Make sure Railway backend is running

---

### Issue 2: CORS Error

**Error in console:**
```
Access to fetch at '...' has been blocked by CORS policy
```

**Shouldn't happen** (already configured), but if it does:

**Check:** Backend CORS allows `https://*.vercel.app`

---

### Issue 3: Blank Page

**Check:**
1. Browser console for JavaScript errors
2. Vercel deployment logs for build errors
3. Refresh page (Ctrl+Shift+R)

---

### Issue 4: 401 Unauthorized Errors

**Expected for protected routes** when not logged in

**Fix:** Register/login first

---

### Issue 5: API Calls Going to Wrong URL

**Check environment variable:**
- Vercel dashboard → Project → Settings → Environment Variables
- `VITE_API_URL` should be: `https://writers-platform-production.up.railway.app/api`

**If wrong:** Update and redeploy

---

## 📊 Quick Test Report

After testing, report status:

**What works:** ✅
- List what's working

**What doesn't work:** ❌
- List any issues

**Console errors:**
- Copy any error messages

**Next steps:**
- If all works: Tell Claude Cloud "All tests passed!"
- If issues: Share error messages for debugging

---

## 🎯 After All Tests Pass

Once everything works:

1. ✅ Factory frontend is production-ready
2. ✅ Claude Cloud can proceed with Session 3
3. ✅ Community frontend will be next

**Congratulations!** 🎉

---

**Testing started:** [Your timestamp]
**Vercel URL:** [Your deployment URL]
**Status:** [Pass/Fail/In Progress]
