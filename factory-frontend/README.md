# Writers Factory - Frontend

React + TypeScript frontend for the Writers Factory AI writing workspace.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Routing
- **TanStack Query** - Data fetching
- **Zustand** - State management
- **Axios** - HTTP client
- **Headless UI** - UI components
- **Heroicons** - Icons

## Features

- **Authentication** - Login/register with JWT
- **Project Management** - Create, edit, delete projects
- **File Upload** - Drag-and-drop support for DOCX, PDF, TXT
- **Scene Editor** - Rich text editing with auto-save
- **AI Analysis** - Multi-agent AI analysis with real-time progress
- **Results Visualization** - Detailed scoring and comparison

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
2. Set root directory to `factory-frontend`
3. Configure environment variable: `VITE_API_URL`
4. Deploy
5. Update backend CORS with Vercel domain

See `../DEPLOYMENT.md` for full deployment guide.

## Project Structure

```
factory-frontend/
├── src/
│   ├── api/           # API client and endpoints
│   ├── components/    # Reusable UI components
│   ├── pages/         # Page components
│   ├── store/         # Zustand state management
│   ├── types/         # TypeScript type definitions
│   ├── App.tsx        # Main app with routing
│   └── index.css      # Global styles
├── vercel.json        # Vercel config
└── package.json       # Dependencies
```

## License

Copyright (c) 2025 Writers Platform
