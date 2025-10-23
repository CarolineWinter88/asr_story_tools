"""对话相关的Schema"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.dialogue import DialogueType, DialogueStatus


class DialogueBase(BaseModel):
    """对话基础Schema"""
    content: str = Field(..., min_length=1, description="对话内容")
    type: DialogueType = Field(default=DialogueType.DIALOGUE, description="段落类型")
    order_index: int = Field(..., ge=0, description="段落顺序")


class DialogueCreate(DialogueBase):
    """创建对话Schema"""
    chapter_id: int = Field(..., description="所属章节ID")
    character_id: Optional[int] = Field(None, description="说话角色ID")


class DialogueUpdate(BaseModel):
    """更新对话Schema"""
    content: Optional[str] = Field(None, min_length=1, description="对话内容")
    character_id: Optional[int] = Field(None, description="说话角色ID")
    type: Optional[DialogueType] = Field(None, description="段落类型")
    order_index: Optional[int] = Field(None, ge=0, description="段落顺序")
    status: Optional[DialogueStatus] = Field(None, description="生成状态")


class DialogueBatchUpdate(BaseModel):
    """批量更新对话Schema"""
    dialogue_ids: list[int] = Field(..., description="对话ID列表")
    character_id: Optional[int] = Field(None, description="统一分配角色ID")
    status: Optional[DialogueStatus] = Field(None, description="批量更新状态")


class DialogueInDB(DialogueBase):
    """数据库中的对话Schema"""
    id: int
    chapter_id: int
    character_id: Optional[int]
    start_time: float
    end_time: float
    audio_path: Optional[str]
    status: DialogueStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DialogueListItem(BaseModel):
    """对话列表项Schema"""
    id: int
    chapter_id: int
    character_id: Optional[int]
    character_name: Optional[str] = None
    content: str
    type: DialogueType
    order_index: int
    status: DialogueStatus
    audio_path: Optional[str]

    class Config:
        from_attributes = True

