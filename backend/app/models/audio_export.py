"""音频导出记录模型"""
from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AudioExport(Base):
    """音频导出记录模型"""
    __tablename__ = "audio_exports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, comment="所属项目ID")
    format = Column(String(50), nullable=False, comment="导出格式 (mp3/wav/m4a/ogg)")
    quality = Column(String(50), comment="音质设置 (320/192/128 kbps)")
    file_path = Column(String(500), nullable=False, comment="文件路径")
    file_size = Column(BigInteger, comment="文件大小(字节)")
    export_range = Column(
        JSON,
        comment="导出范围配置 {chapter_ids: [], from_chapter: int, to_chapter: int}"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关联关系
    project = relationship("Project", back_populates="audio_exports")

