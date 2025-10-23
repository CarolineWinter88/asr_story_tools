"""音频处理服务"""
from typing import List, Optional, Dict
from pathlib import Path
import os
from pydub import AudioSegment
from sqlalchemy.orm import Session

from app.models.dialogue import Dialogue
from app.models.character import Character
from app.models.audio_export import AudioExport
from app.services.tts_factory import TTSFactory
from app.services.tts_base import TTSConfig, TTSResult


class AudioService:
    """音频生成和处理服务"""
    
    def __init__(self, storage_path: str):
        """
        初始化音频服务
        
        Args:
            storage_path: 存储根目录
        """
        self.storage_path = Path(storage_path)
        self.audio_dir = self.storage_path / "audio"
        self.temp_dir = self.storage_path / "temp"
        
        # 确保目录存在
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_dialogue_audio(
        self,
        dialogue: Dialogue,
        character: Optional[Character],
        db: Session
    ) -> TTSResult:
        """
        生成单条对话的音频
        
        Args:
            dialogue: 对话对象
            character: 角色对象（如果是旁白可以为None）
            db: 数据库会话
            
        Returns:
            TTSResult: 生成结果
        """
        # 确定TTS配置
        if character and character.voice_config:
            voice_config = character.voice_config
        else:
            # 旁白使用默认配置
            voice_config = {
                "engine": "mock",
                "voice_id": "mock_narrator",
                "speed": 1.0,
                "pitch": 1.0,
                "volume": 1.0
            }
        
        # 创建TTS配置
        tts_config = TTSConfig(
            engine=voice_config.get("engine", "mock"),
            voice_id=voice_config.get("voice_id", ""),
            speed=voice_config.get("speed", 1.0),
            pitch=voice_config.get("pitch", 1.0),
            volume=voice_config.get("volume", 1.0),
            format="mp3"
        )
        
        # 生成输出路径
        output_dir = self.audio_dir / str(dialogue.chapter_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"dialogue_{dialogue.id}.mp3"
        
        # 创建TTS提供商
        provider = TTSFactory.create_provider(tts_config.engine)
        
        # 生成音频
        result = await provider.synthesize(
            text=dialogue.content,
            config=tts_config,
            output_path=str(output_path)
        )
        
        # 更新对话记录
        if result.success:
            dialogue.audio_path = str(output_path)
            dialogue.duration = result.duration
            dialogue.status = "completed"
        else:
            dialogue.status = "failed"
        
        db.commit()
        
        return result
    
    async def batch_generate(
        self,
        dialogue_ids: List[int],
        db: Session,
        progress_callback=None
    ) -> Dict:
        """
        批量生成对话音频
        
        Args:
            dialogue_ids: 对话ID列表
            db: 数据库会话
            progress_callback: 进度回调函数
            
        Returns:
            生成统计信息
        """
        total = len(dialogue_ids)
        success_count = 0
        failed_count = 0
        failed_items = []
        
        for idx, dialogue_id in enumerate(dialogue_ids):
            # 获取对话和角色
            dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
            if not dialogue:
                failed_count += 1
                failed_items.append({"id": dialogue_id, "error": "对话不存在"})
                continue
            
            character = None
            if dialogue.character_id:
                character = db.query(Character).filter(
                    Character.id == dialogue.character_id
                ).first()
            
            # 生成音频
            try:
                result = await self.generate_dialogue_audio(dialogue, character, db)
                if result.success:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_items.append({
                        "id": dialogue_id,
                        "error": result.error_message
                    })
            except Exception as e:
                failed_count += 1
                failed_items.append({"id": dialogue_id, "error": str(e)})
            
            # 调用进度回调
            if progress_callback:
                progress_callback(idx + 1, total)
        
        return {
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "failed_items": failed_items
        }
    
    def merge_audio_files(
        self,
        audio_paths: List[str],
        output_path: str,
        format: str = "mp3",
        add_silence: int = 500
    ) -> bool:
        """
        合并多个音频文件
        
        Args:
            audio_paths: 音频文件路径列表
            output_path: 输出文件路径
            format: 输出格式
            add_silence: 每段之间插入的静音时长（毫秒）
            
        Returns:
            是否成功
        """
        try:
            combined = AudioSegment.empty()
            silence = AudioSegment.silent(duration=add_silence)
            
            for audio_path in audio_paths:
                if not os.path.exists(audio_path):
                    continue
                
                audio = AudioSegment.from_file(audio_path)
                combined += audio + silence
            
            # 导出合并后的音频
            combined.export(output_path, format=format)
            return True
        except Exception as e:
            print(f"音频合并失败: {str(e)}")
            return False
    
    async def export_chapter_audio(
        self,
        chapter_id: int,
        db: Session,
        format: str = "mp3",
        quality: str = "high"
    ) -> Optional[str]:
        """
        导出整章音频
        
        Args:
            chapter_id: 章节ID
            db: 数据库会话
            format: 导出格式
            quality: 音质 (low/medium/high)
            
        Returns:
            导出文件路径
        """
        # 获取章节的所有对话（按顺序）
        dialogues = db.query(Dialogue).filter(
            Dialogue.chapter_id == chapter_id,
            Dialogue.status == "completed"
        ).order_by(Dialogue.order_index).all()
        
        if not dialogues:
            return None
        
        # 收集音频文件路径
        audio_paths = [d.audio_path for d in dialogues if d.audio_path]
        
        if not audio_paths:
            return None
        
        # 生成输出路径
        output_dir = self.audio_dir / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"chapter_{chapter_id}.{format}"
        
        # 合并音频
        success = self.merge_audio_files(
            audio_paths,
            str(output_path),
            format=format
        )
        
        return str(output_path) if success else None
    
    async def export_project_audio(
        self,
        project_id: int,
        chapter_ids: Optional[List[int]],
        db: Session,
        format: str = "mp3",
        quality: str = "high"
    ) -> Optional[AudioExport]:
        """
        导出项目音频
        
        Args:
            project_id: 项目ID
            chapter_ids: 要导出的章节ID列表（None表示全部）
            db: 数据库会话
            format: 导出格式
            quality: 音质
            
        Returns:
            AudioExport记录
        """
        # 获取要导出的章节
        from app.models.chapter import Chapter
        query = db.query(Chapter).filter(Chapter.project_id == project_id)
        
        if chapter_ids:
            query = query.filter(Chapter.id.in_(chapter_ids))
        
        chapters = query.order_by(Chapter.order_index).all()
        
        if not chapters:
            return None
        
        # 收集所有音频文件
        all_audio_paths = []
        for chapter in chapters:
            dialogues = db.query(Dialogue).filter(
                Dialogue.chapter_id == chapter.id,
                Dialogue.status == "completed"
            ).order_by(Dialogue.order_index).all()
            
            for dialogue in dialogues:
                if dialogue.audio_path:
                    all_audio_paths.append(dialogue.audio_path)
        
        if not all_audio_paths:
            return None
        
        # 生成输出路径
        output_dir = self.audio_dir / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"project_{project_id}.{format}"
        
        # 合并音频
        success = self.merge_audio_files(
            all_audio_paths,
            str(output_path),
            format=format
        )
        
        if not success:
            return None
        
        # 创建导出记录
        file_size = os.path.getsize(output_path)
        export_record = AudioExport(
            project_id=project_id,
            format=format,
            quality=quality,
            file_path=str(output_path),
            file_size=file_size,
            export_range={"chapter_ids": chapter_ids or [c.id for c in chapters]}
        )
        db.add(export_record)
        db.commit()
        db.refresh(export_record)
        
        return export_record
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            for file in self.temp_dir.glob("*"):
                if file.is_file():
                    file.unlink()
        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")

