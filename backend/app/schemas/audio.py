"""音频相关的Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List


class AudioGenerateRequest(BaseModel):
    """音频生成请求"""
    dialogue_id: int = Field(..., description="对话ID")


class AudioBatchGenerateRequest(BaseModel):
    """批量音频生成请求"""
    dialogue_ids: List[int] = Field(..., description="对话ID列表")


class AudioExportRequest(BaseModel):
    """音频导出请求"""
    project_id: int = Field(..., description="项目ID")
    chapter_ids: Optional[List[int]] = Field(None, description="章节ID列表（None表示全部）")
    format: str = Field("mp3", description="导出格式")
    quality: str = Field("high", description="音质")


class AudioGenerateResponse(BaseModel):
    """音频生成响应"""
    dialogue_id: int
    audio_path: Optional[str] = None
    duration: Optional[int] = None
    status: str

