from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    return JSONResponse(
        content={"status": "healthy", "service": "RFTIP API"},
        status_code=200
    )

@router.get("/database")
async def database_health():
    try:
        return JSONResponse(
            content={"status": "connected", "database": "MySQL"},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "detail": str(e)},
            status_code=503
        )
