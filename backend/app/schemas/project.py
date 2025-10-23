"""项目相关的Schema"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    """项目基础Schema"""
    name: str = Field(..., min_length=1, max_length=255, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片路径")


class ProjectCreate(ProjectBase):
    """创建项目Schema"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片路径")
    status: Optional[ProjectStatus] = Field(None, description="项目状态")


class ProjectInDB(ProjectBase):
    """数据库中的项目Schema"""
    id: int
    status: ProjectStatus
    chapters_count: int
    characters_count: int
    total_duration: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListItem(BaseModel):
    """项目列表项Schema"""
    id: int
    name: str
    description: Optional[str]
    cover_image: Optional[str]
    status: ProjectStatus
    chapters_count: int
    characters_count: int
    total_duration: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

