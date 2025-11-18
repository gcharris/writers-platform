from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.core.database import Base, engine
from app.routes import auth, works, reading, comments, ratings, browse, profile, engagement, notifications, dashboard, reading_lists, professional, factory, events, projects, analysis, workflows, knowledge_graph, copilot, notebooklm

# Initialize Sentry for error monitoring
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=0.1,  # Profile 10% of transactions
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        # Send traces for these operations
        send_default_pii=False,  # Don't send personal data by default
        attach_stacktrace=True,
        # Release tracking
        release=f"writers-platform@{settings.VERSION}",
    )

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
        "http://localhost:3000",
        "https://writerscommunity.app",
        "https://www.writerscommunity.app",
        "https://writersfactory.app",
        "https://www.writersfactory.app",
        "https://feisty-passion-production-a7f1.up.railway.app",
        # Vercel deployments (specific domains - wildcards don't work with CORS)
        "https://writers-platform.vercel.app",
        "https://writers-platform-git-main-writers-app-development.vercel.app",
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
# Factory integration
app.include_router(projects.router, prefix=settings.API_PREFIX)
app.include_router(analysis.router, prefix=settings.API_PREFIX)
app.include_router(workflows.router, prefix=settings.API_PREFIX)
# Knowledge Graph
app.include_router(knowledge_graph.router, prefix=settings.API_PREFIX)
# AI Copilot
app.include_router(copilot.router, prefix=settings.API_PREFIX)
# NotebookLM MCP Integration (Phase 9)
app.include_router(notebooklm.router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    return {"message": "Writers Community API", "version": settings.VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
