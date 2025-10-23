"""文本解析服务"""
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import docx
from PyPDF2 import PdfReader


class TextParser:
    """文本解析器"""
    
    # 章节标题识别模式
    CHAPTER_PATTERNS = [
        r'^第[零一二三四五六七八九十百千0-9]+章\s*.+',
        r'^第[零一二三四五六七八九十百千0-9]+节\s*.+',
        r'^Chapter\s+\d+',
        r'^\d+[\.\、]\s*.+',
        r'^[零一二三四五六七八九十百千]+[\.\、]\s*.+',
    ]
    
    # 对话标记识别模式
    DIALOGUE_PATTERNS = [
        r'(.+?)说：["""](.+?)["""]',
        r'(.+?)道：["""](.+?)["""]',
        r'(.+?)：["""](.+?)["""]',
        r'"(.+?)"，(.+?)说',
    ]
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """
        读取文件内容
        支持 TXT, DOCX, PDF
        """
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        
        if extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif extension == '.docx':
            doc = docx.Document(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        
        elif extension == '.pdf':
            reader = PdfReader(file_path)
            text = []
            for page in reader.pages:
                text.append(page.extract_text())
            return '\n'.join(text)
        
        else:
            raise ValueError(f"不支持的文件格式: {extension}")
    
    @classmethod
    def split_chapters(cls, text: str) -> List[Dict[str, any]]:
        """
        智能分割章节
        返回: [{'title': '章节标题', 'content': '章节内容', 'order_index': 序号}]
        """
        chapters = []
        lines = text.split('\n')
        
        current_chapter = None
        current_content = []
        order_index = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是章节标题
            is_chapter_title = False
            for pattern in cls.CHAPTER_PATTERNS:
                if re.match(pattern, line):
                    is_chapter_title = True
                    break
            
            if is_chapter_title:
                # 保存上一章
                if current_chapter:
                    current_chapter['content'] = '\n'.join(current_content)
                    current_chapter['word_count'] = len(current_chapter['content'])
                    chapters.append(current_chapter)
                
                # 开始新章节
                current_chapter = {
                    'title': line,
                    'order_index': order_index,
                }
                current_content = []
                order_index += 1
            else:
                # 添加到当前章节内容
                if current_chapter is not None:
                    current_content.append(line)
        
        # 保存最后一章
        if current_chapter:
            current_chapter['content'] = '\n'.join(current_content)
            current_chapter['word_count'] = len(current_chapter['content'])
            chapters.append(current_chapter)
        
        # 如果没有识别到章节，整个文本作为一章
        if not chapters:
            chapters.append({
                'title': '正文',
                'content': text,
                'order_index': 0,
                'word_count': len(text)
            })
        
        return chapters
    
    @classmethod
    def extract_dialogues(cls, text: str) -> List[Dict[str, any]]:
        """
        提取对话和旁白
        返回: [{'type': 'dialogue/narration', 'character': '角色名', 'content': '内容', 'order_index': 序号}]
        """
        dialogues = []
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        for idx, para in enumerate(paragraphs):
            # 尝试匹配对话模式
            character_name = None
            dialogue_content = None
            
            for pattern in cls.DIALOGUE_PATTERNS:
                match = re.search(pattern, para)
                if match:
                    groups = match.groups()
                    if len(groups) >= 2:
                        # 判断哪个是角色名，哪个是对话内容
                        if len(groups[0]) < len(groups[1]):
                            character_name = groups[0].strip()
                            dialogue_content = groups[1].strip()
                        else:
                            character_name = groups[1].strip()
                            dialogue_content = groups[0].strip()
                    break
            
            # 构造对话/旁白对象
            if character_name and dialogue_content:
                dialogues.append({
                    'type': 'dialogue',
                    'character': character_name,
                    'content': dialogue_content,
                    'order_index': idx
                })
            else:
                # 旁白
                dialogues.append({
                    'type': 'narration',
                    'character': None,
                    'content': para,
                    'order_index': idx
                })
        
        return dialogues
    
    @classmethod
    def extract_characters(cls, dialogues: List[Dict[str, any]]) -> List[str]:
        """
        从对话列表中提取角色名称
        返回: 去重后的角色名列表
        """
        characters = set()
        for dialogue in dialogues:
            if dialogue.get('character'):
                characters.add(dialogue['character'])
        
        return sorted(list(characters))
    
    @staticmethod
    def estimate_duration(text: str, words_per_second: float = 3.5) -> int:
        """
        估算文本朗读时长（秒）
        中文平均语速约 3-4 字/秒
        """
        word_count = len(text)
        duration = int(word_count / words_per_second)
        return duration

