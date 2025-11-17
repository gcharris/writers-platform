# Writers Community - Frontend

React + TypeScript frontend for the Writers Community public reading platform.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS 3** - Styling
- **React Router 7** - Routing
- **TanStack Query** - Data fetching
- **Zustand** - State management
- **Axios** - HTTP client
- **Headless UI** - UI components
- **Heroicons** - Icons

## Features

- **Badge System** - AI-analyzed, human-verified, self-certified, community uploads
- **Public Browsing** - No auth required to read works
- **Badge Filtering** - Filter works by badge type
- **Work Reading** - Full-text reader with comments and likes
- **Direct Upload** - Upload manuscripts with AI detection
- **Factory Integration** - CTAs to Writers Factory throughout
- **Authentication** - Login/register for uploading and commenting

## Development

### Prerequisites

- Node.js 18+
- Backend API running (see `../backend/README.md`)

### Setup

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Update .env with your backend API URL
# VITE_API_URL=http://localhost:8000/api

# Start development server
npm run dev
```

Visit http://localhost:5173

### Environment Variables

```bash
VITE_API_URL=http://localhost:8000/api  # Backend API URL
```

For production (Vercel):
```bash
VITE_API_URL=https://writers-platform-production.up.railway.app/api
```

## Deployment to Vercel

1. Connect GitHub repository to Vercel
2. Set root directory to `community-frontend`
3. Configure environment variable: `VITE_API_URL`
4. Deploy
5. Update backend CORS with Vercel domain

See `../DEPLOYMENT.md` for full deployment guide.

## Project Structure

```
community-frontend/
├── src/
│   ├── api/           # API client and endpoints
│   ├── components/    # Badge system, Layout
│   ├── pages/         # Home, Browse, ViewWork, Upload, Login, Register
│   ├── store/         # Auth state
│   ├── types/         # TypeScript definitions
│   ├── App.tsx        # Main app with routing
│   └── index.css      # Global styles
├── vercel.json        # Vercel config
└── package.json       # Dependencies
```

## Key Pages

- **Home** (`/`) - Landing page with badge explainer and CTAs
- **Browse** (`/browse`) - Public works list with filtering
- **ViewWork** (`/works/:id`) - Read full work with comments
- **Upload** (`/upload`) - Upload manuscript with AI detection
- **Login/Register** - Authentication

## License

Copyright (c) 2025 Writers Platform
