"""TTS服务抽象基类"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class TTSConfig:
    """TTS配置"""
    engine: str  # azure, aliyun, tencent, etc.
    voice_id: str  # 音色ID
    speed: float = 1.0  # 语速 (0.5-2.0)
    pitch: float = 1.0  # 音调 (0.5-2.0)
    volume: float = 1.0  # 音量 (0.5-2.0)
    sample_rate: int = 16000  # 采样率
    format: str = "mp3"  # 音频格式


@dataclass
class TTSResult:
    """TTS生成结果"""
    success: bool
    audio_path: Optional[str] = None
    duration: Optional[int] = None  # 音频时长（秒）
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None


class TTSProvider(ABC):
    """TTS服务提供商抽象基类"""
    
    def __init__(self, api_key: str = None, region: str = None, **kwargs):
        """
        初始化TTS提供商
        
        Args:
            api_key: API密钥
            region: 服务区域
            **kwargs: 其他配置参数
        """
        self.api_key = api_key
        self.region = region
        self.config = kwargs
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        config: TTSConfig,
        output_path: str
    ) -> TTSResult:
        """
        合成语音
        
        Args:
            text: 要合成的文本
            config: TTS配置
            output_path: 输出文件路径
            
        Returns:
            TTSResult: 合成结果
        """
        pass
    
    @abstractmethod
    async def get_available_voices(self) -> List[Dict]:
        """
        获取可用的音色列表
        
        Returns:
            音色列表，每个音色包含: {id, name, gender, language, description}
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        测试连接是否正常
        
        Returns:
            连接状态
        """
        pass
    
    def validate_config(self, config: TTSConfig) -> bool:
        """
        验证配置是否有效
        
        Args:
            config: TTS配置
            
        Returns:
            配置是否有效
        """
        if not config.voice_id:
            return False
        if not (0.5 <= config.speed <= 2.0):
            return False
        if not (0.5 <= config.pitch <= 2.0):
            return False
        if not (0.5 <= config.volume <= 2.0):
            return False
        return True


class MockTTSProvider(TTSProvider):
    """
    Mock TTS提供商（用于开发测试）
    生成静音音频文件
    """
    
    async def synthesize(
        self,
        text: str,
        config: TTSConfig,
        output_path: str
    ) -> TTSResult:
        """生成Mock音频（静音）"""
        try:
            from pydub import AudioSegment
            from pydub.generators import Sine
            
            # 根据文字数量估算时长（3.5字/秒）
            duration_ms = int(len(text) / 3.5 * 1000)
            
            # 生成静音音频
            silence = AudioSegment.silent(duration=duration_ms)
            
            # 保存文件
            silence.export(output_path, format=config.format)
            
            return TTSResult(
                success=True,
                audio_path=output_path,
                duration=int(duration_ms / 1000),
                metadata={"engine": "mock", "text_length": len(text)}
            )
        except Exception as e:
            return TTSResult(
                success=False,
                error_message=f"Mock TTS生成失败: {str(e)}"
            )
    
    async def get_available_voices(self) -> List[Dict]:
        """返回Mock音色列表"""
        return [
            {
                "id": "mock_male_1",
                "name": "测试男声1",
                "gender": "male",
                "language": "zh-CN",
                "description": "Mock测试音色"
            },
            {
                "id": "mock_female_1",
                "name": "测试女声1",
                "gender": "female",
                "language": "zh-CN",
                "description": "Mock测试音色"
            }
        ]
    
    async def test_connection(self) -> bool:
        """Mock连接总是成功"""
        return True

