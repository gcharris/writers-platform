# Admin Panel Implementation Plan

## Overview
Build a comprehensive admin dashboard for platform administrators to manage users, content, and monitor system health.

## Current Infrastructure

### Existing
- ✓ User `role` field in database (defaults to "writer")
- ✓ Writer Dashboard API (`/api/dashboard/stats`)
- ✓ Factory Dashboard (project management)
- ✓ Authentication system with JWT
- ✓ Sentry integration for error tracking

### Missing
- Admin-only API routes with role-based access control
- Admin panel frontend
- User management interface
- Content moderation tools
- Platform analytics dashboard

---

## Phase 1: Backend - Admin API Routes

### 1.1 Role-Based Access Control

**File:** `backend/app/core/permissions.py`

```python
from fastapi import HTTPException, Depends
from app.routes.auth import get_current_user
from app.models.user import User

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role for endpoint access."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

### 1.2 Admin User Management API

**File:** `backend/app/routes/admin/users.py`

**Endpoints:**
- `GET /api/admin/users` - List all users (paginated, searchable)
- `GET /api/admin/users/{user_id}` - Get user details
- `PATCH /api/admin/users/{user_id}/role` - Update user role
- `PATCH /api/admin/users/{user_id}/status` - Ban/suspend/activate user
- `DELETE /api/admin/users/{user_id}` - Delete user account
- `GET /api/admin/users/{user_id}/activity` - View user activity log

**Schemas:**
```python
class UserListResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    status: str  # active, suspended, banned
    works_count: int
    created_at: datetime
    last_login: datetime | None

class UserRoleUpdate(BaseModel):
    role: str  # writer, admin, moderator

class UserStatusUpdate(BaseModel):
    status: str  # active, suspended, banned
    reason: str | None
```

### 1.3 Content Moderation API

**File:** `backend/app/routes/admin/moderation.py`

**Endpoints:**
- `GET /api/admin/works/flagged` - List flagged works
- `GET /api/admin/works/{work_id}` - Review work details
- `DELETE /api/admin/works/{work_id}` - Remove work
- `PATCH /api/admin/works/{work_id}/flag` - Flag/unflag work
- `GET /api/admin/comments/flagged` - List flagged comments
- `DELETE /api/admin/comments/{comment_id}` - Remove comment
- `GET /api/admin/reports` - View user reports
- `PATCH /api/admin/reports/{report_id}` - Resolve report

**New Models:**
```python
# backend/app/models/report.py
class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID, ForeignKey("users.id"))
    content_type = Column(String)  # work, comment, user
    content_id = Column(UUID)
    reason = Column(String)
    description = Column(Text)
    status = Column(String)  # pending, resolved, dismissed
    resolved_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
```

### 1.4 Platform Analytics API

**File:** `backend/app/routes/admin/analytics.py`

**Endpoints:**
- `GET /api/admin/analytics/overview` - Platform statistics
- `GET /api/admin/analytics/users` - User growth metrics
- `GET /api/admin/analytics/content` - Content statistics
- `GET /api/admin/analytics/engagement` - Engagement metrics
- `GET /api/admin/analytics/errors` - Error logs (from Sentry)

**Response Examples:**
```python
class PlatformOverview(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    total_works: int
    works_today: int
    total_comments: int
    total_ratings: int
    avg_rating: float

class UserGrowthMetrics(BaseModel):
    date: str
    new_users: int
    active_users: int
    churned_users: int
```

### 1.5 System Health API

**File:** `backend/app/routes/admin/system.py`

**Endpoints:**
- `GET /api/admin/system/health` - Database, API, external services status
- `GET /api/admin/system/errors` - Recent error logs
- `GET /api/admin/system/jobs` - Background job status
- `POST /api/admin/system/cleanup` - Trigger data cleanup tasks
- `GET /api/admin/system/metrics` - Performance metrics

---

## Phase 2: Frontend - Admin Dashboard

### 2.1 Admin Routes Structure

**New Pages:**
```
community-frontend/src/pages/admin/
├── AdminDashboard.tsx       # Main overview
├── UsersManagement.tsx      # User list and management
├── ContentModeration.tsx    # Review flagged content
├── PlatformAnalytics.tsx    # Charts and metrics
└── SystemHealth.tsx         # Status monitoring
```

**Route Configuration:**
```typescript
// App.tsx - Add admin routes
<Route path="/admin" element={<AdminLayout />}>
  <Route index element={<AdminDashboard />} />
  <Route path="users" element={<UsersManagement />} />
  <Route path="moderation" element={<ContentModeration />} />
  <Route path="analytics" element={<PlatformAnalytics />} />
  <Route path="system" element={<SystemHealth />} />
</Route>
```

### 2.2 Admin Dashboard Overview

**File:** `community-frontend/src/pages/admin/AdminDashboard.tsx`

**Features:**
- Platform statistics cards
  - Total users / active today / new this week
  - Total works / published today
  - Comments, ratings, engagement metrics
- Quick actions
  - Review flagged content
  - View recent reports
  - Check system health
- Recent activity feed
  - New user registrations
  - Content published
  - Moderation actions taken
- Charts
  - User growth over time
  - Content publication trends
  - Engagement metrics

**Dependencies:**
```bash
npm install recharts  # For charts
npm install @tanstack/react-table  # For data tables
npm install date-fns  # For date formatting
```

### 2.3 User Management Interface

**File:** `community-frontend/src/pages/admin/UsersManagement.tsx`

**Features:**
- User list table
  - Search by username/email
  - Filter by role (admin, writer, suspended, banned)
  - Sort by date joined, last active, works count
  - Pagination
- User actions
  - View profile details
  - Change role (writer ↔ admin)
  - Suspend/ban user
  - Delete account
  - View activity history
- Bulk actions
  - Export user list to CSV
  - Bulk role updates

**UI Components:**
```typescript
interface UserRow {
  id: string;
  username: string;
  email: string;
  role: 'writer' | 'admin';
  status: 'active' | 'suspended' | 'banned';
  worksCount: number;
  createdAt: string;
  lastLogin: string | null;
}

// Table columns
- Avatar
- Username (clickable to view profile)
- Email
- Role badge
- Status badge
- Works count
- Joined date
- Last active
- Actions dropdown (Edit Role, Suspend, Delete)
```

### 2.4 Content Moderation Interface

**File:** `community-frontend/src/pages/admin/ContentModeration.tsx`

**Features:**
- Flagged content tabs
  - Works
  - Comments
  - User reports
- Review interface
  - Content preview
  - Reporter information
  - Reason for flag
  - Action buttons (Approve, Remove, Ban Author)
- Moderation history
  - Recent actions taken
  - Who took the action
  - Timestamp

**Report Flow:**
```
1. User flags content
2. Admin sees in flagged queue
3. Admin reviews content
4. Admin takes action:
   - Approve (unflag)
   - Remove content
   - Suspend author
   - Ban author
5. Report marked as resolved
```

### 2.5 Platform Analytics Dashboard

**File:** `community-frontend/src/pages/admin/PlatformAnalytics.tsx`

**Features:**
- Date range selector (Last 7 days, 30 days, 90 days, All time)
- User metrics
  - Growth chart (new users over time)
  - Active users (DAU, WAU, MAU)
  - User retention rate
  - Churn rate
- Content metrics
  - Works published over time
  - Top genres
  - Average word count
  - Publication rate
- Engagement metrics
  - Comments per work
  - Ratings distribution
  - Most engaged users
  - Peak activity hours
- Export options
  - Download as CSV
  - Generate PDF report

**Charts:**
```typescript
// Using recharts
import { LineChart, BarChart, PieChart, AreaChart } from 'recharts';

- User growth: Line chart
- Content by genre: Pie chart
- Engagement over time: Area chart
- Top users: Bar chart
```

### 2.6 System Health Monitor

**File:** `community-frontend/src/pages/admin/SystemHealth.tsx`

**Features:**
- Status indicators
  - Database: ✓ Connected
  - API: ✓ Healthy
  - External Services: ✓ All operational
- Recent errors
  - Error message
  - Stack trace
  - Count of occurrences
  - Link to Sentry
- Background jobs
  - AI analysis queue
  - Email notifications
  - Database cleanup
- Performance metrics
  - API response times
  - Database query performance
  - Memory usage
- Manual actions
  - Clear cache
  - Run database cleanup
  - Restart background workers
  - Test external connections

---

## Phase 3: Database Updates

### 3.1 New Tables

**Reports Table:**
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reporter_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL,  -- 'work', 'comment', 'user'
    content_id UUID NOT NULL,
    reason VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'resolved', 'dismissed'
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_content ON reports(content_type, content_id);
```

**Moderation Actions Table:**
```sql
CREATE TABLE moderation_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    moderator_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,  -- 'remove_work', 'suspend_user', 'ban_user', etc.
    target_type VARCHAR(50) NOT NULL,
    target_id UUID NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_moderation_actions_moderator ON moderation_actions(moderator_id);
CREATE INDEX idx_moderation_actions_target ON moderation_actions(target_type, target_id);
```

**User Status Updates:**
```sql
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';
ALTER TABLE users ADD COLUMN suspended_until TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN suspension_reason TEXT NULL;
ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL;

CREATE INDEX idx_users_status ON users(status);
```

**Work Flags:**
```sql
ALTER TABLE works ADD COLUMN flagged BOOLEAN DEFAULT FALSE;
ALTER TABLE works ADD COLUMN flag_reason TEXT NULL;
ALTER TABLE works ADD COLUMN flagged_at TIMESTAMP NULL;
ALTER TABLE works ADD COLUMN flagged_by UUID REFERENCES users(id);

CREATE INDEX idx_works_flagged ON works(flagged) WHERE flagged = TRUE;
```

### 3.2 Migrations

**File:** `backend/alembic/versions/xxxx_add_admin_features.py`

```python
"""Add admin panel features

Revision ID: xxxx
Revises: previous_revision
Create Date: 2025-11-18
"""

def upgrade():
    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', UUID(), nullable=False),
        # ... (see schema above)
    )

    # Create moderation_actions table
    op.create_table(
        'moderation_actions',
        # ... (see schema above)
    )

    # Update users table
    op.add_column('users', sa.Column('status', sa.String(20), server_default='active'))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))

    # Update works table
    op.add_column('works', sa.Column('flagged', sa.Boolean(), server_default='false'))
```

---

## Phase 4: Security & Access Control

### 4.1 Admin Role Assignment

**Initial Setup:**
```python
# Script to promote first user to admin
# backend/scripts/create_admin.py

from app.core.database import SessionLocal
from app.models.user import User

def create_admin(email: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.role = "admin"
        db.commit()
        print(f"✓ {user.username} is now an admin")
    else:
        print(f"✗ User with email {email} not found")
    db.close()

if __name__ == "__main__":
    create_admin("your@email.com")
```

**Run:**
```bash
cd backend
python scripts/create_admin.py
```

### 4.2 Frontend Route Protection

**File:** `community-frontend/src/components/AdminRoute.tsx`

```typescript
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function AdminRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((state) => state.user);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-red-600 mb-4">Access Denied</h1>
          <p className="text-gray-600">You don't have permission to access this page.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
```

### 4.3 Admin Navigation

**Update:** `community-frontend/src/components/Layout.tsx`

Add admin link to navigation (only visible to admins):

```typescript
{user?.role === 'admin' && (
  <Link
    to="/admin"
    className="text-gray-700 hover:text-sky-600 font-medium"
  >
    Admin Panel
  </Link>
)}
```

---

## Phase 5: UI/UX Design

### 5.1 Admin Layout

**File:** `community-frontend/src/components/AdminLayout.tsx`

```typescript
- Sidebar navigation
  - Dashboard
  - Users
  - Content Moderation
  - Analytics
  - System Health
- Top bar
  - Search
  - Notifications
  - Admin profile
  - Back to Community
```

### 5.2 Color Scheme

```css
/* Admin panel uses different colors to distinguish from main site */
--admin-primary: #dc2626;      /* red-600 */
--admin-secondary: #7c3aed;    /* violet-600 */
--admin-success: #16a34a;      /* green-600 */
--admin-warning: #f59e0b;      /* amber-500 */
--admin-danger: #dc2626;       /* red-600 */
```

### 5.3 Components

**New Components:**
- `AdminCard` - Statistics cards
- `DataTable` - Sortable, filterable table
- `StatusBadge` - User/content status indicators
- `ActionButton` - Quick action buttons
- `ConfirmDialog` - Confirmation for destructive actions
- `MetricChart` - Reusable chart component

---

## Implementation Timeline

### Week 1: Backend Foundation
- Day 1-2: Role-based access control + User management API
- Day 3-4: Content moderation API + Database migrations
- Day 5: Analytics API + System health API

### Week 2: Frontend Core
- Day 1-2: Admin layout + Dashboard overview
- Day 3-4: User management interface
- Day 5: Content moderation interface

### Week 3: Analytics & Polish
- Day 1-2: Platform analytics dashboard
- Day 3: System health monitor
- Day 4-5: Testing, bug fixes, documentation

---

## Testing Checklist

### Backend
- [ ] Admin routes return 403 for non-admin users
- [ ] User role updates work correctly
- [ ] Content moderation actions persist
- [ ] Analytics calculations are accurate
- [ ] System health checks work

### Frontend
- [ ] Admin panel is hidden from non-admin users
- [ ] User search and filtering work
- [ ] Content moderation flows correctly
- [ ] Charts render properly with real data
- [ ] Responsive design on mobile

### Security
- [ ] All admin routes require authentication
- [ ] Role checks prevent privilege escalation
- [ ] Sensitive data is not exposed in APIs
- [ ] Actions are logged for audit trail

---

## Future Enhancements

### Phase 6: Advanced Features
- **Email Campaigns**: Send announcements to users
- **A/B Testing**: Test platform changes
- **Advanced Analytics**: Cohort analysis, funnel tracking
- **AI Content Detection**: Automated spam/inappropriate content detection
- **Bulk Operations**: CSV import/export, bulk user actions
- **Audit Logs**: Detailed history of all admin actions
- **Role Permissions**: Granular permission system (moderator vs admin)

### Phase 7: Automation
- **Auto-moderation**: AI-powered content flagging
- **Scheduled Reports**: Weekly analytics emails
- **Alert System**: Notifications for platform issues
- **Workflow Automation**: Auto-suspend users after X violations

---

## API Documentation

All admin endpoints will be documented in FastAPI's auto-generated docs at:
```
https://writers-platform-production.up.railway.app/api/docs#admin
```

---

## Success Metrics

### Platform Health
- Response time for admin operations < 500ms
- 100% uptime for admin panel
- All admin actions logged for audit

### User Management
- Ability to manage 10,000+ users efficiently
- Search results in < 200ms
- Bulk operations complete in < 5s

### Content Moderation
- Flagged content review time < 5 minutes
- Moderation action success rate > 99%
- False positive rate < 5%

---

## Notes

- Admin panel should be built incrementally
- Start with most critical features (user management, content moderation)
- Add analytics and monitoring later
- Always test with production-like data volumes
- Consider privacy implications of admin access to user data
- Log all admin actions for compliance and audit trails
