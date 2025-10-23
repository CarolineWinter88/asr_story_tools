"""角色管理API"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.response import success_response
from app.core.exceptions import NotFoundException
from app.models.character import Character
from app.models.project import Project
from app.models.chapter import Chapter
from app.models.dialogue import Dialogue
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterInDB, CharacterListItem
from app.services.text_parser import TextParser

router = APIRouter()


@router.post("/extract", response_model=dict)
async def extract_characters(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """
    自动提取项目中的所有角色
    从章节内容中识别对话角色
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException(message=f"项目 ID {project_id} 不存在")
    
    # 获取项目的所有章节
    chapters = db.query(Chapter).filter(Chapter.project_id == project_id).all()
    
    if not chapters:
        return success_response(
            data={"characters": [], "count": 0},
            message="该项目暂无章节，无法提取角色"
        )
    
    # 提取所有角色
    all_characters = set()
    for chapter in chapters:
        if chapter.content:
            dialogues = TextParser.extract_dialogues(chapter.content)
            characters = TextParser.extract_characters(dialogues)
            all_characters.update(characters)
    
    # 保存角色到数据库（避免重复）
    existing_characters = db.query(Character).filter(
        Character.project_id == project_id
    ).all()
    existing_names = {c.name for c in existing_characters}
    
    new_characters = []
    for char_name in all_characters:
        if char_name not in existing_names:
            new_char = Character(
                project_id=project_id,
                name=char_name,
                voice_config={
                    "engine": "azure",
                    "voice_id": "",
                    "speed": 1.0,
                    "pitch": 1.0,
                    "volume": 1.0
                }
            )
            db.add(new_char)
            new_characters.append(new_char)
    
    # 更新项目的角色数量
    project.characters_count = len(existing_characters) + len(new_characters)
    
    db.commit()
    
    # 刷新数据
    for char in new_characters:
        db.refresh(char)
    
    return success_response(
        data={
            "extracted_count": len(all_characters),
            "new_count": len(new_characters),
            "existing_count": len(existing_characters),
            "characters": [CharacterListItem.model_validate(c).model_dump() for c in new_characters]
        },
        message=f"成功提取 {len(new_characters)} 个新角色"
    )


@router.get("/", response_model=dict)
async def list_characters(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """获取项目的角色列表"""
    characters = db.query(Character).filter(
        Character.project_id == project_id
    ).all()
    
    items = [CharacterListItem.model_validate(c) for c in characters]
    
    return success_response(
        data={"items": [item.model_dump() for item in items]},
        message="获取角色列表成功"
    )


@router.get("/{character_id}", response_model=dict)
async def get_character(character_id: int, db: Session = Depends(get_db)):
    """获取角色详情"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise NotFoundException(message=f"角色 ID {character_id} 不存在")
    
    return success_response(
        data=CharacterInDB.model_validate(character).model_dump(),
        message="获取角色详情成功"
    )


@router.post("/", response_model=dict)
async def create_character(
    character_data: CharacterCreate,
    db: Session = Depends(get_db)
):
    """创建新角色"""
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == character_data.project_id).first()
    if not project:
        raise NotFoundException(message=f"项目 ID {character_data.project_id} 不存在")
    
    # 转换voice_config为dict
    data_dict = character_data.model_dump()
    if 'voice_config' in data_dict and data_dict['voice_config']:
        data_dict['voice_config'] = data_dict['voice_config']
    
    new_character = Character(**data_dict)
    db.add(new_character)
    
    # 更新项目角色数量
    project.characters_count = db.query(Character).filter(
        Character.project_id == character_data.project_id
    ).count() + 1
    
    db.commit()
    db.refresh(new_character)
    
    return success_response(
        data=CharacterInDB.model_validate(new_character).model_dump(),
        message="创建角色成功"
    )


@router.put("/{character_id}", response_model=dict)
async def update_character(
    character_id: int,
    character_data: CharacterUpdate,
    db: Session = Depends(get_db)
):
    """更新角色信息（包括声音配置）"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise NotFoundException(message=f"角色 ID {character_id} 不存在")
    
    # 更新字段
    update_data = character_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)
    
    db.commit()
    db.refresh(character)
    
    return success_response(
        data=CharacterInDB.model_validate(character).model_dump(),
        message="更新角色成功"
    )


@router.delete("/{character_id}", response_model=dict)
async def delete_character(character_id: int, db: Session = Depends(get_db)):
    """删除角色"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise NotFoundException(message=f"角色 ID {character_id} 不存在")
    
    project_id = character.project_id
    db.delete(character)
    
    # 更新项目角色数量
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        project.characters_count = db.query(Character).filter(
            Character.project_id == project_id
        ).count()
    
    db.commit()
    
    return success_response(message="删除角色成功")


@router.get("/{character_id}/statistics", response_model=dict)
async def get_character_statistics(character_id: int, db: Session = Depends(get_db)):
    """获取角色统计信息"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise NotFoundException(message=f"角色 ID {character_id} 不存在")
    
    # 统计对话数量
    dialogue_count = db.query(func.count(Dialogue.id)).filter(
        Dialogue.character_id == character_id
    ).scalar()
    
    # 更新角色的对话数量
    character.dialogue_count = dialogue_count
    db.commit()
    
    statistics = {
        "character_id": character.id,
        "character_name": character.name,
        "dialogue_count": dialogue_count,
        "total_duration": character.total_duration,
        "voice_config": character.voice_config
    }
    
    return success_response(data=statistics, message="获取角色统计成功")

