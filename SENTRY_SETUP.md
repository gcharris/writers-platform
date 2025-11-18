# Sentry Error Monitoring Setup

**Status**: ✅ Integrated (Optional - Enable with DSN)

Error monitoring is now integrated into all three applications using Sentry. This provides:
- Real-time error tracking
- Performance monitoring
- Session replay for debugging
- Stack traces and user context

---

## Quick Setup (5 minutes)

### 1. Create Sentry Account (Free)

1. Go to [sentry.io](https://sentry.io) and sign up
2. Create a new organization (e.g., "Writers Platform")
3. Create three projects:
   - **Backend API** (Platform: Python/FastAPI)
   - **Factory Frontend** (Platform: React)
   - **Community Frontend** (Platform: React)

### 2. Get DSN Keys

After creating each project, Sentry will show you a **DSN** (Data Source Name). It looks like:
```
https://abc123@o123456.ingest.sentry.io/456789
```

Copy the DSN for each project.

### 3. Configure Backend (Railway)

Add these environment variables to Railway:

```bash
SENTRY_DSN=https://your-backend-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # Optional: defaults to 10%
```

### 4. Configure Factory Frontend (Vercel)

Add these environment variables to Vercel (Factory deployment):

```bash
VITE_SENTRY_DSN=https://your-factory-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT=production
```

### 5. Configure Community Frontend (Vercel)

Add these environment variables to Vercel (Community deployment):

```bash
VITE_SENTRY_DSN=https://your-community-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT=production
```

---

## What Gets Tracked

### Backend (FastAPI)
- ✅ Unhandled exceptions
- ✅ API endpoint errors
- ✅ Database query errors (via SqlalchemyIntegration)
- ✅ Performance traces (10% sample rate)
- ✅ Release version tracking

### Frontend (React)
- ✅ JavaScript errors
- ✅ Unhandled promise rejections
- ✅ Component render errors
- ✅ Network request failures
- ✅ Performance monitoring (10% sample rate)
- ✅ Session Replay (10% normal, 100% on errors)

---

## Privacy & Performance

### What We DON'T Send
- ❌ Personal identifiable information (PII)
- ❌ User passwords or tokens
- ❌ Full request/response bodies by default

### Sampling Rates
- **Performance Traces**: 10% of transactions
- **Session Replays**: 10% of normal sessions, 100% with errors
- **Error Capture**: 100% of errors

These rates keep Sentry costs low while providing excellent coverage.

---

## Testing Sentry

### Backend Test
```python
# Add this to any endpoint temporarily
from sentry_sdk import capture_exception

try:
    1 / 0
except Exception as e:
    capture_exception(e)
```

### Frontend Test
```typescript
// Add this to any component temporarily
throw new Error("Test Sentry error");
```

After triggering the error, check your Sentry dashboard (Issues tab) within 1-2 minutes.

---

## Features Enabled

### 🔍 Error Tracking
- Real-time error notifications
- Stack traces with source maps
- Breadcrumbs showing user actions before error
- Release tracking (shows which deployment had the error)

### 📊 Performance Monitoring
- API endpoint performance (p50, p75, p95)
- Frontend page load times
- Database query performance
- Slow transaction alerts

### 🎥 Session Replay
- Watch user sessions that encountered errors
- See exactly what the user clicked
- Debug hard-to-reproduce issues
- Privacy-safe (no sensitive data captured)

---

## Disabling Sentry

If you don't want to use Sentry:
- Simply don't set the `SENTRY_DSN` / `VITE_SENTRY_DSN` environment variables
- The apps will run normally without error tracking
- No performance impact when disabled

---

## Cost

Sentry offers a **free tier** that includes:
- 5,000 errors/month
- 10,000 performance units/month
- 50 replay sessions/month

For our sampling rates (10%), this is plenty for MVP/early production.

Paid plans start at $26/month if you exceed free tier limits.

---

## Advanced Configuration

### Custom Error Contexts
```python
# Backend: Add user context
from sentry_sdk import set_user
set_user({"id": user.id, "username": user.username})
```

```typescript
// Frontend: Add user context
Sentry.setUser({ id: user.id, username: user.username });
```

### Custom Tags
```python
# Backend
from sentry_sdk import set_tag
set_tag("feature", "knowledge_graph")
```

### Filtering Errors
Edit `backend/app/main.py` or frontend `main.tsx` to add `before_send`:
```python
def before_send(event, hint):
    # Filter out certain errors
    if 'expected_error' in str(hint.get('exc_info', '')):
        return None
    return event

sentry_sdk.init(dsn=..., before_send=before_send)
```

---

## Monitoring Checklist

Once enabled, set up these alerts in Sentry:

- [ ] Error spike alert (>10 errors/hour)
- [ ] New error type alert
- [ ] Performance regression alert (p95 >2s)
- [ ] Weekly error summary email

---

## Integration Status

| Component | Status | Config Required | Notes |
|-----------|--------|-----------------|-------|
| Backend API | ✅ Integrated | `SENTRY_DSN` | FastAPI + SQLAlchemy |
| Factory Frontend | ✅ Integrated | `VITE_SENTRY_DSN` | React + Router |
| Community Frontend | ✅ Integrated | `VITE_SENTRY_DSN` | React + Router |

---

**Next Step**: Create Sentry account and add DSN to Railway/Vercel environment variables!

**Estimated Time**: 5 minutes per project (15 minutes total)
