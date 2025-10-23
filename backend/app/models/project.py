"""项目数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    """项目状态枚举"""
    DRAFT = "draft"  # 草稿
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成


class Project(Base):
    """项目模型"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment="项目名称")
    description = Column(Text, comment="项目描述")
    cover_image = Column(String(500), comment="封面图片路径")
    status = Column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.DRAFT,
        nullable=False,
        comment="项目状态"
    )
    chapters_count = Column(Integer, default=0, comment="章节数量")
    characters_count = Column(Integer, default=0, comment="角色数量")
    total_duration = Column(Integer, default=0, comment="总时长(秒)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关联关系
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    audio_exports = relationship("AudioExport", back_populates="project", cascade="all, delete-orphan")

