"""章节数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ChapterStatus(str, enum.Enum):
    """章节状态枚举"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    ERROR = "error"  # 处理出错


class Chapter(Base):
    """章节模型"""
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="所属项目ID")
    title = Column(String(500), nullable=False, comment="章节标题")
    order_index = Column(Integer, nullable=False, comment="章节顺序")
    content = Column(Text, comment="原始文本内容")
    word_count = Column(Integer, default=0, comment="字数统计")
    status = Column(
        SQLEnum(ChapterStatus),
        default=ChapterStatus.PENDING,
        nullable=False,
        comment="章节状态"
    )
    duration = Column(Integer, default=0, comment="时长(秒)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关联关系
    project = relationship("Project", back_populates="chapters")
    dialogues = relationship("Dialogue", back_populates="chapter", cascade="all, delete-orphan")

