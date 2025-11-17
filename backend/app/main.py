from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routes import auth, works, reading, comments, ratings, browse, profile, engagement, notifications, dashboard, reading_lists, professional, factory, events

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://writerscommunity.app",
        "https://www.writerscommunity.app",
        "https://feisty-passion-production-a7f1.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(works.router, prefix=settings.API_PREFIX)
app.include_router(reading.router, prefix=settings.API_PREFIX)
app.include_router(comments.router, prefix=settings.API_PREFIX)
app.include_router(ratings.router, prefix=settings.API_PREFIX)
# Sprint 3: Discovery routes
app.include_router(browse.router, prefix=settings.API_PREFIX)
app.include_router(profile.router, prefix=settings.API_PREFIX)
app.include_router(engagement.router, prefix=settings.API_PREFIX)
# Sprint 4: Notifications and community
app.include_router(notifications.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)
app.include_router(reading_lists.router, prefix=settings.API_PREFIX)
# Sprint 5: Professional pipeline
app.include_router(professional.router, prefix=settings.API_PREFIX)
app.include_router(factory.router, prefix=settings.API_PREFIX)
app.include_router(events.router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {"message": "Writers Community API", "version": settings.VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
