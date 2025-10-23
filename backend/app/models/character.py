"""角色数据模型"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Character(Base):
    """角色模型"""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="所属项目ID")
    name = Column(String(255), nullable=False, comment="角色名称")
    avatar = Column(String(500), comment="角色头像路径")
    description = Column(Text, comment="角色描述")
    dialogue_count = Column(Integer, default=0, comment="对话数量")
    total_duration = Column(Integer, default=0, comment="总时长(秒)")
    voice_config = Column(
        JSON,
        comment="声音配置 JSON {engine, voice_id, speed, pitch, volume, emotion}"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关联关系
    project = relationship("Project", back_populates="characters")
    dialogues = relationship("Dialogue", back_populates="character")

