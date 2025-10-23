"""角色相关的Schema"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class VoiceConfig(BaseModel):
    """声音配置Schema"""
    engine: str = Field(default="azure", description="TTS引擎")
    voice_id: str = Field(..., description="声音ID")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="语速")
    pitch: float = Field(default=1.0, ge=0.5, le=2.0, description="音调")
    volume: float = Field(default=1.0, ge=0.0, le=2.0, description="音量")
    emotion: Optional[str] = Field(None, description="情感类型")


class CharacterBase(BaseModel):
    """角色基础Schema"""
    name: str = Field(..., min_length=1, max_length=255, description="角色名称")
    avatar: Optional[str] = Field(None, max_length=500, description="角色头像")
    description: Optional[str] = Field(None, description="角色描述")


class CharacterCreate(CharacterBase):
    """创建角色Schema"""
    project_id: int = Field(..., description="所属项目ID")
    voice_config: Optional[VoiceConfig] = Field(None, description="声音配置")


class CharacterUpdate(BaseModel):
    """更新角色Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="角色名称")
    avatar: Optional[str] = Field(None, max_length=500, description="角色头像")
    description: Optional[str] = Field(None, description="角色描述")
    voice_config: Optional[Dict[str, Any]] = Field(None, description="声音配置")


class CharacterInDB(CharacterBase):
    """数据库中的角色Schema"""
    id: int
    project_id: int
    dialogue_count: int
    total_duration: int
    voice_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CharacterListItem(BaseModel):
    """角色列表项Schema"""
    id: int
    project_id: int
    name: str
    avatar: Optional[str]
    dialogue_count: int
    total_duration: int
    voice_config: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

