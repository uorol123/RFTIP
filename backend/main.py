"""
RFTIP 后端应用主入口

RadarFusionTrack Intelligence Platform - Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import get_settings
from core.database import Base, engine
from app.routers import health, auth, files, tracks, zones, analysis, query


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    description="雷达轨迹监测与智能分析平台 API"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动时创建数据库表"""
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    """根路径 - API 状态"""
    return {
        "message": "RFTIP API is running",
        "version": settings.app_version,
        "status": "online"
    }


# 注册路由
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(tracks.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(query.router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
