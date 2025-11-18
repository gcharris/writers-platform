# Password Reset Implementation Plan

## Current Status
- ✓ Login pages have "Forgot password?" links
- ✗ No backend API routes
- ✗ No frontend pages
- ✗ No email sending configured

---

## Architecture Overview

### Flow
1. User clicks "Forgot password?" on login page
2. User enters email address
3. Backend generates secure reset token
4. Backend sends email with reset link
5. User clicks link in email → opens reset page with token
6. User enters new password
7. Backend validates token and updates password
8. User redirected to login

---

## Phase 1: Backend Implementation

### 1.1 Database Schema

**New Model:** `backend/app/models/password_reset.py`

```python
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from datetime import datetime, timedelta

from app.core.database import Base

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Migration:**
```sql
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reset_tokens_user ON password_reset_tokens(user_id);
CREATE INDEX idx_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_reset_tokens_expires ON password_reset_tokens(expires_at);
```

### 1.2 Email Service

**File:** `backend/app/core/email.py`

```python
from typing import List
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# OR use SMTP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    """Email service supporting multiple providers."""

    @staticmethod
    def send_password_reset(to_email: str, reset_link: str, username: str):
        """Send password reset email."""
        subject = "Reset Your Password - Writers Platform"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4F46E5;">Reset Your Password</h2>
                <p>Hi {username},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <div style="margin: 30px 0; text-align: center;">
                    <a href="{reset_link}"
                       style="background-color: #4F46E5; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    This link will expire in 1 hour. If you didn't request this, you can safely ignore this email.
                </p>
                <p style="color: #666; font-size: 14px;">
                    If the button doesn't work, copy and paste this link into your browser:<br>
                    <a href="{reset_link}">{reset_link}</a>
                </p>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                <p style="color: #999; font-size: 12px;">
                    Writers Platform Team<br>
                    This is an automated message, please do not reply.
                </p>
            </div>
        </body>
        </html>
        """

        # Option 1: SendGrid
        if os.getenv("SENDGRID_API_KEY"):
            message = Mail(
                from_email=os.getenv("FROM_EMAIL", "noreply@writersplatform.com"),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
            sg.send(message)

        # Option 2: SMTP (Gmail, etc.)
        elif os.getenv("SMTP_HOST"):
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = os.getenv("FROM_EMAIL", "noreply@writersplatform.com")
            msg['To'] = to_email

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", 587))) as server:
                server.starttls()
                server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
                server.send_message(msg)
        else:
            # Development: Log to console
            print(f"\n{'='*60}")
            print(f"PASSWORD RESET EMAIL")
            print(f"To: {to_email}")
            print(f"Reset Link: {reset_link}")
            print(f"{'='*60}\n")
```

**Environment Variables:**
```bash
# SendGrid (recommended for production)
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=noreply@writersplatform.com

# OR SMTP (Gmail, etc.)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your@gmail.com

# Frontend URL for reset links
FRONTEND_URL=https://www.writerscommunity.app
```

### 1.3 API Routes

**File:** `backend/app/routes/auth.py` (add these endpoints)

```python
import secrets
from datetime import datetime, timedelta
from app.models.password_reset import PasswordResetToken
from app.core.email import EmailService

# Request password reset
@router.post("/forgot-password")
async def forgot_password(
    email: EmailStr,
    db: Session = Depends(get_db)
):
    """Request password reset email."""

    # Find user by email
    user = db.query(User).filter(User.email == email).first()

    # Always return success (don't reveal if email exists)
    if not user:
        return {"message": "If that email exists, a reset link has been sent"}

    # Generate secure token
    token = secrets.token_urlsafe(32)

    # Create reset token record
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(reset_token)
    db.commit()

    # Send email
    frontend_url = settings.FRONTEND_URL or "http://localhost:5173"
    reset_link = f"{frontend_url}/reset-password?token={token}"

    EmailService.send_password_reset(
        to_email=user.email,
        reset_link=reset_link,
        username=user.username
    )

    return {"message": "If that email exists, a reset link has been sent"}


# Verify reset token
@router.get("/reset-password/verify/{token}")
async def verify_reset_token(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify if reset token is valid."""

    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()

    if not reset_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )

    return {"valid": True}


# Reset password
@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """Reset password using token."""

    # Validate token
    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()

    if not reset_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )

    # Validate password
    if len(new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )

    # Update user password
    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = get_password_hash(new_password)

    # Mark token as used
    reset_record.used = True

    db.commit()

    return {"message": "Password reset successful"}
```

**Schemas:**
```python
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
```

### 1.4 Config Updates

**File:** `backend/app/core/config/__init__.py`

```python
class Settings(BaseSettings):
    # ... existing fields ...

    # Email configuration
    SENDGRID_API_KEY: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@writersplatform.com"

    # Frontend URL for reset links
    FRONTEND_URL: Optional[str] = None
```

---

## Phase 2: Frontend Implementation

### 2.1 Forgot Password Page

**File:** `community-frontend/src/pages/ForgotPassword.tsx`

```typescript
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { authApi } from '../api/community';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authApi.forgotPassword(email);
      setSuccess(true);
    } catch (err: any) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-blue-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center">
          <div className="mb-4">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Check Your Email</h2>
          <p className="text-gray-600 mb-6">
            If an account exists with <strong>{email}</strong>, we've sent password reset instructions.
          </p>
          <Link
            to="/login"
            className="inline-block px-6 py-3 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
          >
            Back to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Forgot Password?
          </h1>
          <p className="text-gray-600">
            Enter your email and we'll send you reset instructions
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                placeholder="your@email.com"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-sky-600 text-white py-3 rounded-lg font-medium hover:bg-sky-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <Link to="/login" className="text-sky-600 hover:text-sky-700 font-medium">
              ← Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 2.2 Reset Password Page

**File:** `community-frontend/src/pages/ResetPassword.tsx`

```typescript
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import { authApi } from '../api/community';

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [validToken, setValidToken] = useState(false);
  const [error, setError] = useState('');

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setError('Invalid reset link');
        setVerifying(false);
        return;
      }

      try {
        await authApi.verifyResetToken(token);
        setValidToken(true);
      } catch (err) {
        setError('This reset link is invalid or has expired');
      } finally {
        setVerifying(false);
      }
    };

    verifyToken();
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await authApi.resetPassword(token!, password);
      navigate('/login', {
        state: { message: 'Password reset successful! Please log in.' }
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (verifying) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-blue-50 flex items-center justify-center px-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verifying reset link...</p>
        </div>
      </div>
    );
  }

  if (!validToken) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-blue-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center">
          <div className="mb-4">
            <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Invalid Reset Link</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link
            to="/forgot-password"
            className="inline-block px-6 py-3 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
          >
            Request New Link
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Reset Password
          </h1>
          <p className="text-gray-600">Enter your new password</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                  placeholder="At least 6 characters"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                  placeholder="Re-enter your password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showConfirmPassword ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-sky-600 text-white py-3 rounded-lg font-medium hover:bg-sky-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
```

### 2.3 API Updates

**File:** `community-frontend/src/api/community.ts`

```typescript
// Auth API additions
export const authApi = {
  // ... existing methods ...

  forgotPassword: async (email: string) => {
    const response = await apiClient.post('/auth/forgot-password', { email });
    return response.data;
  },

  verifyResetToken: async (token: string) => {
    const response = await apiClient.get(`/auth/reset-password/verify/${token}`);
    return response.data;
  },

  resetPassword: async (token: string, newPassword: string) => {
    const response = await apiClient.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    });
    return response.data;
  },
};
```

### 2.4 Route Configuration

**File:** `community-frontend/src/App.tsx`

```typescript
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

// Add routes
<Route path="/forgot-password" element={<ForgotPassword />} />
<Route path="/reset-password" element={<ResetPassword />} />
```

---

## Phase 3: Testing

### Backend Tests
```bash
# Test forgot password endpoint
curl -X POST http://localhost:8000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Test reset password
curl -X POST http://localhost:8000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "TOKEN_HERE", "new_password": "newpass123"}'
```

### Frontend Tests
1. Go to `/forgot-password`
2. Enter email
3. Check console for reset link (dev mode)
4. Click reset link
5. Enter new password
6. Verify can log in with new password

---

## Dependencies

### Backend
```bash
# Add to requirements.txt
sendgrid==6.11.0  # If using SendGrid

# Or for SMTP (usually built-in)
# No additional deps needed
```

### Frontend
No additional dependencies needed (uses existing packages)

---

## Security Considerations

1. **Token Security**
   - Use cryptographically secure random tokens (`secrets.token_urlsafe`)
   - Tokens expire after 1 hour
   - Single-use tokens (marked as `used` after reset)
   - Store token hash instead of plain token (optional enhancement)

2. **Rate Limiting**
   - Limit reset requests per email (e.g., 3 per hour)
   - Prevent brute force token guessing

3. **Email Validation**
   - Don't reveal if email exists (same message for all requests)
   - Validate email format on backend

4. **Password Requirements**
   - Minimum 6 characters (can increase)
   - Consider adding complexity requirements

---

## Deployment Checklist

### Railway (Backend)
- [ ] Add email environment variables
- [ ] Run database migration
- [ ] Test email sending in production
- [ ] Set FRONTEND_URL to production domain

### Vercel (Frontend)
- [ ] Deploy updated frontend
- [ ] Test forgot password flow
- [ ] Test reset password flow
- [ ] Verify emails are received

---

## Email Provider Setup

### Option 1: SendGrid (Recommended)
1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Create API key
3. Verify sender email
4. Add to Railway environment:
   ```
   SENDGRID_API_KEY=your_key_here
   FROM_EMAIL=noreply@yourdomain.com
   ```

### Option 2: Gmail SMTP
1. Enable 2-factor auth on Gmail
2. Generate app password
3. Add to Railway environment:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your@gmail.com
   SMTP_PASSWORD=your_app_password
   FROM_EMAIL=your@gmail.com
   ```

### Option 3: Development (Console Logging)
- No setup needed
- Reset links printed to console
- Good for testing

---

## Timeline

### Estimated Time: 4-6 hours
- Backend (2-3 hours): Models, routes, email service, migration
- Frontend (1-2 hours): Pages, API integration, routes
- Testing (1 hour): Flow testing, email testing, edge cases

---

## Future Enhancements

1. **Security**
   - Add rate limiting
   - Hash tokens before storing
   - Add CAPTCHA to forgot password form

2. **UX**
   - Email template customization
   - SMS password reset option
   - Password strength indicator
   - Success animations

3. **Admin**
   - View reset token usage in admin panel
   - Manually expire tokens
   - Monitor abuse/spam

---

## Notes

- Always use HTTPS in production
- Test email deliverability before launch
- Monitor email bounce rates
- Consider email reputation/SPF/DKIM setup
- Keep reset link expiry short (1 hour recommended)
