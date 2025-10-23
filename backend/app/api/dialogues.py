"""对话编辑API"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success_response
from app.core.exceptions import NotFoundException
from app.models.dialogue import Dialogue
from app.models.character import Character
from app.models.chapter import Chapter
from app.schemas.dialogue import (
    DialogueCreate,
    DialogueUpdate,
    DialogueBatchUpdate,
    DialogueInDB,
    DialogueListItem
)

router = APIRouter()


@router.get("/", response_model=dict)
async def list_dialogues(
    chapter_id: int = Query(..., description="章节ID"),
    db: Session = Depends(get_db)
):
    """获取章节的对话列表"""
    dialogues = db.query(Dialogue).filter(
        Dialogue.chapter_id == chapter_id
    ).order_by(Dialogue.order_index).all()
    
    # 关联角色名称
    items = []
    for dialogue in dialogues:
        item_dict = DialogueListItem.model_validate(dialogue).model_dump()
        if dialogue.character_id:
            character = db.query(Character).filter(
                Character.id == dialogue.character_id
            ).first()
            if character:
                item_dict['character_name'] = character.name
        items.append(item_dict)
    
    return success_response(
        data={"items": items},
        message="获取对话列表成功"
    )


@router.get("/{dialogue_id}", response_model=dict)
async def get_dialogue(dialogue_id: int, db: Session = Depends(get_db)):
    """获取对话详情"""
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    if not dialogue:
        raise NotFoundException(message=f"对话 ID {dialogue_id} 不存在")
    
    return success_response(
        data=DialogueInDB.model_validate(dialogue).model_dump(),
        message="获取对话详情成功"
    )


@router.post("/", response_model=dict)
async def create_dialogue(
    dialogue_data: DialogueCreate,
    db: Session = Depends(get_db)
):
    """创建新对话段落"""
    # 检查章节是否存在
    chapter = db.query(Chapter).filter(Chapter.id == dialogue_data.chapter_id).first()
    if not chapter:
        raise NotFoundException(message=f"章节 ID {dialogue_data.chapter_id} 不存在")
    
    # 检查角色是否存在（如果指定了）
    if dialogue_data.character_id:
        character = db.query(Character).filter(
            Character.id == dialogue_data.character_id
        ).first()
        if not character:
            raise NotFoundException(message=f"角色 ID {dialogue_data.character_id} 不存在")
    
    new_dialogue = Dialogue(**dialogue_data.model_dump())
    db.add(new_dialogue)
    db.commit()
    db.refresh(new_dialogue)
    
    return success_response(
        data=DialogueInDB.model_validate(new_dialogue).model_dump(),
        message="创建对话成功"
    )


@router.post("/batch", response_model=dict)
async def create_dialogues_batch(
    chapter_id: int = Query(..., description="章节ID"),
    db: Session = Depends(get_db)
):
    """
    批量创建对话（从章节内容自动提取）
    """
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException(message=f"章节 ID {chapter_id} 不存在")
    
    if not chapter.content:
        return success_response(
            data={"dialogues": [], "count": 0},
            message="章节内容为空，无法提取对话"
        )
    
    # 使用文本解析器提取对话
    from app.services.text_parser import TextParser
    dialogues_data = TextParser.extract_dialogues(chapter.content)
    
    # 获取角色映射（角色名 -> 角色ID）
    characters = db.query(Character).filter(
        Character.project_id == chapter.project_id
    ).all()
    character_map = {c.name: c.id for c in characters}
    
    # 批量创建对话
    created_dialogues = []
    for dialogue_data in dialogues_data:
        character_id = None
        if dialogue_data.get('character'):
            character_id = character_map.get(dialogue_data['character'])
        
        new_dialogue = Dialogue(
            chapter_id=chapter_id,
            character_id=character_id,
            type=dialogue_data['type'],
            content=dialogue_data['content'],
            order_index=dialogue_data['order_index']
        )
        db.add(new_dialogue)
        created_dialogues.append(new_dialogue)
    
    db.commit()
    
    # 刷新数据
    for dialogue in created_dialogues:
        db.refresh(dialogue)
    
    return success_response(
        data={
            "count": len(created_dialogues),
            "dialogues": [DialogueInDB.model_validate(d).model_dump() for d in created_dialogues]
        },
        message=f"成功创建 {len(created_dialogues)} 条对话"
    )


@router.put("/{dialogue_id}", response_model=dict)
async def update_dialogue(
    dialogue_id: int,
    dialogue_data: DialogueUpdate,
    db: Session = Depends(get_db)
):
    """更新对话内容"""
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    if not dialogue:
        raise NotFoundException(message=f"对话 ID {dialogue_id} 不存在")
    
    # 更新字段
    update_data = dialogue_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dialogue, field, value)
    
    db.commit()
    db.refresh(dialogue)
    
    return success_response(
        data=DialogueInDB.model_validate(dialogue).model_dump(),
        message="更新对话成功"
    )


@router.put("/batch/update", response_model=dict)
async def update_dialogues_batch(
    batch_data: DialogueBatchUpdate,
    db: Session = Depends(get_db)
):
    """批量更新对话"""
    if not batch_data.dialogue_ids:
        return success_response(data={"updated_count": 0}, message="未指定要更新的对话")
    
    # 查询要更新的对话
    dialogues = db.query(Dialogue).filter(
        Dialogue.id.in_(batch_data.dialogue_ids)
    ).all()
    
    # 批量更新
    for dialogue in dialogues:
        if batch_data.character_id is not None:
            dialogue.character_id = batch_data.character_id
        if batch_data.status is not None:
            dialogue.status = batch_data.status
    
    db.commit()
    
    return success_response(
        data={"updated_count": len(dialogues)},
        message=f"成功更新 {len(dialogues)} 条对话"
    )


@router.delete("/{dialogue_id}", response_model=dict)
async def delete_dialogue(dialogue_id: int, db: Session = Depends(get_db)):
    """删除对话"""
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    if not dialogue:
        raise NotFoundException(message=f"对话 ID {dialogue_id} 不存在")
    
    db.delete(dialogue)
    db.commit()
    
    return success_response(message="删除对话成功")

