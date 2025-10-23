"""音频生成与导出API"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.core.response import success_response
from app.core.exceptions import NotFoundException
from app.models.dialogue import Dialogue
from app.models.character import Character
from app.models.chapter import Chapter
from app.models.audio_export import AudioExport
from app.schemas.audio import (
    AudioGenerateRequest,
    AudioBatchGenerateRequest,
    AudioExportRequest,
    AudioGenerateResponse
)
from app.services.audio_service import AudioService
from app.services.tts_factory import TTSFactory

router = APIRouter()

# 初始化音频服务
audio_service = AudioService(storage_path=settings.STORAGE_PATH)


@router.get("/engines", response_model=dict)
async def get_available_engines():
    """获取可用的TTS引擎列表"""
    engines = TTSFactory.get_available_engines()
    return success_response(
        data={"engines": engines},
        message="获取TTS引擎列表成功"
    )


@router.get("/voices", response_model=dict)
async def get_available_voices(
    engine: str = Query(..., description="TTS引擎名称")
):
    """获取指定引擎的可用音色列表"""
    try:
        provider = TTSFactory.create_provider(engine)
        voices = await provider.get_available_voices()
        return success_response(
            data={"voices": voices},
            message=f"获取{engine}音色列表成功"
        )
    except ValueError as e:
        raise NotFoundException(message=str(e))


@router.post("/generate", response_model=dict)
async def generate_single_audio(
    request: AudioGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    生成单条对话的音频
    """
    # 获取对话
    dialogue = db.query(Dialogue).filter(Dialogue.id == request.dialogue_id).first()
    if not dialogue:
        raise NotFoundException(message=f"对话 ID {request.dialogue_id} 不存在")
    
    # 获取角色（如果有）
    character = None
    if dialogue.character_id:
        character = db.query(Character).filter(
            Character.id == dialogue.character_id
        ).first()
    
    # 生成音频
    dialogue.status = "generating"
    db.commit()
    
    try:
        result = await audio_service.generate_dialogue_audio(dialogue, character, db)
        
        if result.success:
            return success_response(
                data=AudioGenerateResponse(
                    dialogue_id=dialogue.id,
                    audio_path=result.audio_path,
                    duration=result.duration,
                    status="completed"
                ).model_dump(),
                message="音频生成成功"
            )
        else:
            return success_response(
                data={"error": result.error_message},
                message="音频生成失败",
                code=500
            )
    except Exception as e:
        dialogue.status = "failed"
        db.commit()
        return success_response(
            data={"error": str(e)},
            message="音频生成异常",
            code=500
        )


@router.post("/batch-generate", response_model=dict)
async def batch_generate_audio(
    request: AudioBatchGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    批量生成对话音频
    """
    if not request.dialogue_ids:
        return success_response(
            data={"message": "未指定要生成的对话"},
            message="参数错误"
        )
    
    # 在后台任务中执行批量生成
    async def batch_task():
        await audio_service.batch_generate(
            dialogue_ids=request.dialogue_ids,
            db=db
        )
    
    background_tasks.add_task(batch_task)
    
    return success_response(
        data={
            "total": len(request.dialogue_ids),
            "status": "processing"
        },
        message=f"已启动批量生成任务，共 {len(request.dialogue_ids)} 条对话"
    )


@router.post("/export/chapter", response_model=dict)
async def export_chapter_audio(
    chapter_id: int = Query(..., description="章节ID"),
    format: str = Query("mp3", description="导出格式"),
    quality: str = Query("high", description="音质"),
    db: Session = Depends(get_db)
):
    """
    导出整章音频
    """
    # 检查章节是否存在
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException(message=f"章节 ID {chapter_id} 不存在")
    
    # 导出音频
    output_path = await audio_service.export_chapter_audio(
        chapter_id=chapter_id,
        db=db,
        format=format,
        quality=quality
    )
    
    if not output_path:
        return success_response(
            data={"error": "该章节没有已生成的音频"},
            message="导出失败",
            code=400
        )
    
    return success_response(
        data={
            "file_path": output_path,
            "chapter_id": chapter_id,
            "format": format
        },
        message="章节音频导出成功"
    )


@router.post("/export/project", response_model=dict)
async def export_project_audio(
    request: AudioExportRequest,
    db: Session = Depends(get_db)
):
    """
    导出项目音频
    """
    # 导出音频
    export_record = await audio_service.export_project_audio(
        project_id=request.project_id,
        chapter_ids=request.chapter_ids,
        db=db,
        format=request.format,
        quality=request.quality
    )
    
    if not export_record:
        return success_response(
            data={"error": "没有可导出的音频"},
            message="导出失败",
            code=400
        )
    
    return success_response(
        data={
            "export_id": export_record.id,
            "file_path": export_record.file_path,
            "file_size": export_record.file_size,
            "format": export_record.format
        },
        message="项目音频导出成功"
    )


@router.get("/download/{export_id}", response_model=None)
async def download_audio(
    export_id: int,
    db: Session = Depends(get_db)
):
    """
    下载导出的音频文件
    """
    export_record = db.query(AudioExport).filter(AudioExport.id == export_id).first()
    if not export_record:
        raise NotFoundException(message=f"导出记录 ID {export_id} 不存在")
    
    file_path = Path(export_record.file_path)
    if not file_path.exists():
        raise NotFoundException(message="音频文件不存在")
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type=f"audio/{export_record.format}"
    )


@router.get("/exports", response_model=dict)
async def list_exports(
    project_id: Optional[int] = Query(None, description="项目ID"),
    db: Session = Depends(get_db)
):
    """
    获取导出记录列表
    """
    query = db.query(AudioExport)
    
    if project_id:
        query = query.filter(AudioExport.project_id == project_id)
    
    exports = query.order_by(AudioExport.created_at.desc()).all()
    
    items = []
    for export in exports:
        items.append({
            "id": export.id,
            "project_id": export.project_id,
            "format": export.format,
            "quality": export.quality,
            "file_size": export.file_size,
            "created_at": export.created_at.isoformat()
        })
    
    return success_response(
        data={"items": items},
        message="获取导出记录成功"
    )


@router.delete("/exports/{export_id}", response_model=dict)
async def delete_export(
    export_id: int,
    db: Session = Depends(get_db)
):
    """
    删除导出记录和文件
    """
    export_record = db.query(AudioExport).filter(AudioExport.id == export_id).first()
    if not export_record:
        raise NotFoundException(message=f"导出记录 ID {export_id} 不存在")
    
    # 删除文件
    file_path = Path(export_record.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # 删除记录
    db.delete(export_record)
    db.commit()
    
    return success_response(message="删除导出记录成功")

