"""
RFTIP 后端应用主入口

RadarFusionTrack Intelligence Platform - Backend
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import get_settings
from core.database import Base, engine
from core.logging import setup_logging, get_logger
from core.middleware import (
    RequestContextMiddleware,
    SecurityLoggingMiddleware,
    ErrorHandlingMiddleware,
    PerformanceLoggingMiddleware,
)
from core.error_handler import register_exception_handlers
from app.routers import health, auth, files, tracks, zones, analysis, query


settings = get_settings()

# Setup logging first
setup_logging()
logger = get_logger(__name__)

logger.info(f"Starting {settings.app_name} v{settings.app_version}")
logger.info(f"Debug mode: {settings.debug}")
logger.info(f"Environment: {'development' if settings.debug else 'production'}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    # 关闭时执行
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    description="雷达轨迹监测与智能分析平台 API",
    lifespan=lifespan,
)

# Register global exception handlers
register_exception_handlers(app)

# Add custom middleware (order matters - last added is executed first)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(PerformanceLoggingMiddleware, slow_threshold_ms=settings.slow_request_threshold_ms)
app.add_middleware(SecurityLoggingMiddleware)
app.add_middleware(RequestContextMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径 - API 状态"""
    return {
        "success": True,
        "message": "RFTIP API is running",
        "version": settings.app_version,
        "status": "online",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }


# 注册路由
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(tracks.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(query.router, prefix="/api")

logger.info("All routers registered successfully")


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_config=None  # Disable uvicorn's default logging, use our custom config
    )
