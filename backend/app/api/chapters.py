"""章节管理API"""
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import os

from app.core.database import get_db
from app.core.config import settings
from app.core.response import success_response
from app.core.exceptions import NotFoundException, FileUploadException
from app.models.chapter import Chapter
from app.models.project import Project
from app.schemas.chapter import ChapterCreate, ChapterUpdate, ChapterInDB, ChapterListItem
from app.services.text_parser import TextParser

router = APIRouter()


@router.post("/upload", response_model=dict)
async def upload_text_file(
    project_id: int = Form(..., description="项目ID"),
    file: UploadFile = File(..., description="文本文件"),
    auto_split: bool = Form(True, description="是否自动分割章节"),
    db: Session = Depends(get_db)
):
    """
    上传文本文件并自动分割章节
    支持: TXT, DOCX, PDF
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException(message=f"项目 ID {project_id} 不存在")
    
    # 检查文件格式
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ['.txt', '.docx', '.pdf']:
        raise FileUploadException(message=f"不支持的文件格式: {file_ext}")
    
    # 保存文件
    upload_dir = Path(settings.STORAGE_PATH) / "uploads" / str(project_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 读取文件内容
    try:
        text_content = TextParser.read_file(str(file_path))
    except Exception as e:
        raise FileUploadException(message=f"文件读取失败: {str(e)}")
    
    # 自动分割章节
    chapters_data = []
    if auto_split:
        chapters_data = TextParser.split_chapters(text_content)
    else:
        # 不分割，整个文件作为一章
        chapters_data = [{
            'title': file.filename,
            'content': text_content,
            'order_index': 0,
            'word_count': len(text_content)
        }]
    
    # 保存章节到数据库
    created_chapters = []
    for chapter_data in chapters_data:
        new_chapter = Chapter(
            project_id=project_id,
            title=chapter_data['title'],
            content=chapter_data['content'],
            order_index=chapter_data['order_index'],
            word_count=chapter_data['word_count']
        )
        db.add(new_chapter)
        created_chapters.append(new_chapter)
    
    # 更新项目的章节数量
    project.chapters_count = len(created_chapters)
    
    db.commit()
    
    # 刷新数据
    for chapter in created_chapters:
        db.refresh(chapter)
    
    return success_response(
        data={
            "uploaded_file": file.filename,
            "chapters_count": len(created_chapters),
            "chapters": [ChapterListItem.model_validate(c).model_dump() for c in created_chapters]
        },
        message="文件上传并分割成功"
    )


@router.get("/", response_model=dict)
async def list_chapters(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """获取项目的章节列表"""
    chapters = db.query(Chapter).filter(
        Chapter.project_id == project_id
    ).order_by(Chapter.order_index).all()
    
    items = [ChapterListItem.model_validate(c) for c in chapters]
    
    return success_response(
        data={"items": [item.model_dump() for item in items]},
        message="获取章节列表成功"
    )


@router.get("/{chapter_id}", response_model=dict)
async def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """获取章节详情"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException(message=f"章节 ID {chapter_id} 不存在")
    
    return success_response(
        data=ChapterInDB.model_validate(chapter).model_dump(),
        message="获取章节详情成功"
    )


@router.put("/{chapter_id}", response_model=dict)
async def update_chapter(
    chapter_id: int,
    chapter_data: ChapterUpdate,
    db: Session = Depends(get_db)
):
    """更新章节信息"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException(message=f"章节 ID {chapter_id} 不存在")
    
    # 更新字段
    update_data = chapter_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chapter, field, value)
    
    # 更新字数
    if 'content' in update_data:
        chapter.word_count = len(update_data['content'])
    
    db.commit()
    db.refresh(chapter)
    
    return success_response(
        data=ChapterInDB.model_validate(chapter).model_dump(),
        message="更新章节成功"
    )


@router.delete("/{chapter_id}", response_model=dict)
async def delete_chapter(chapter_id: int, db: Session = Depends(get_db)):
    """删除章节"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException(message=f"章节 ID {chapter_id} 不存在")
    
    project_id = chapter.project_id
    db.delete(chapter)
    
    # 更新项目的章节数量
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        project.chapters_count = db.query(Chapter).filter(
            Chapter.project_id == project_id
        ).count()
    
    db.commit()
    
    return success_response(message="删除章节成功")

