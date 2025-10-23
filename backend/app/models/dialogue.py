"""对话/旁白数据模型"""
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DialogueType(str, enum.Enum):
    """对话类型枚举"""
    DIALOGUE = "dialogue"  # 对话
    NARRATION = "narration"  # 旁白


class DialogueStatus(str, enum.Enum):
    """对话状态枚举"""
    PENDING = "pending"  # 待生成
    GENERATING = "generating"  # 生成中
    COMPLETED = "completed"  # 已完成
    ERROR = "error"  # 生成出错


class Dialogue(Base):
    """对话/旁白模型"""
    __tablename__ = "dialogues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, comment="所属章节ID")
    character_id = Column(Integer, ForeignKey("characters.id"), comment="说话角色ID(旁白为NULL)")
    order_index = Column(Integer, nullable=False, comment="段落顺序")
    type = Column(
        SQLEnum(DialogueType),
        default=DialogueType.DIALOGUE,
        nullable=False,
        comment="段落类型"
    )
    content = Column(Text, nullable=False, comment="对话文本内容")
    start_time = Column(Float, default=0.0, comment="开始时间(秒)")
    end_time = Column(Float, default=0.0, comment="结束时间(秒)")
    audio_path = Column(String(500), comment="音频文件路径")
    status = Column(
        SQLEnum(DialogueStatus),
        default=DialogueStatus.PENDING,
        nullable=False,
        comment="生成状态"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关联关系
    chapter = relationship("Chapter", back_populates="dialogues")
    character = relationship("Character", back_populates="dialogues")

