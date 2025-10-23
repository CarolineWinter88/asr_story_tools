"""FastAPI主应用入口"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import BaseAPIException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    print("🚀 正在初始化数据库...")
    init_db()
    print("✅ 数据库初始化完成")
    yield
    # 关闭时清理资源
    print("👋 应用正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI有声书语音合成工具 - 后端API",
    lifespan=lifespan,
)

# 配置CORS中间件（支持局域网访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """处理自定义API异常"""
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    print(f"❌ 未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误" if not settings.DEBUG else str(exc),
            "data": None
        }
    )


# 健康检查端点
@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 注册API路由
from app.api import projects, chapters, characters, dialogues, audio
app.include_router(projects.router, prefix="/api/projects", tags=["项目管理"])
app.include_router(chapters.router, prefix="/api/chapters", tags=["章节管理"])
app.include_router(characters.router, prefix="/api/characters", tags=["角色管理"])
app.include_router(dialogues.router, prefix="/api/dialogues", tags=["对话编辑"])
app.include_router(audio.router, prefix="/api/audio", tags=["音频处理"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

