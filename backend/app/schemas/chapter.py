"""章节相关的Schema"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.chapter import ChapterStatus


class ChapterBase(BaseModel):
    """章节基础Schema"""
    title: str = Field(..., min_length=1, max_length=500, description="章节标题")
    content: Optional[str] = Field(None, description="章节内容")
    order_index: int = Field(..., ge=0, description="章节顺序")


class ChapterCreate(ChapterBase):
    """创建章节Schema"""
    project_id: int = Field(..., description="所属项目ID")


class ChapterUpdate(BaseModel):
    """更新章节Schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="章节标题")
    content: Optional[str] = Field(None, description="章节内容")
    order_index: Optional[int] = Field(None, ge=0, description="章节顺序")
    status: Optional[ChapterStatus] = Field(None, description="章节状态")


class ChapterInDB(ChapterBase):
    """数据库中的章节Schema"""
    id: int
    project_id: int
    word_count: int
    status: ChapterStatus
    duration: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChapterListItem(BaseModel):
    """章节列表项Schema"""
    id: int
    project_id: int
    title: str
    order_index: int
    word_count: int
    status: ChapterStatus
    duration: int
    created_at: datetime

    class Config:
        from_attributes = True

