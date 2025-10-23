"""TTS服务工厂"""
from typing import Dict, Optional
from app.services.tts_base import TTSProvider, MockTTSProvider


class TTSFactory:
    """TTS提供商工厂类"""
    
    # 注册的TTS提供商
    _providers: Dict[str, type] = {
        "mock": MockTTSProvider,
        # 后续可扩展其他引擎:
        # "azure": AzureTTSProvider,
        # "aliyun": AliyunTTSProvider,
        # "tencent": TencentTTSProvider,
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        注册新的TTS提供商
        
        Args:
            name: 提供商名称
            provider_class: 提供商类（必须继承TTSProvider）
        """
        if not issubclass(provider_class, TTSProvider):
            raise ValueError(f"{provider_class} 必须继承 TTSProvider")
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(
        cls,
        engine: str,
        api_key: Optional[str] = None,
        region: Optional[str] = None,
        **kwargs
    ) -> TTSProvider:
        """
        创建TTS提供商实例
        
        Args:
            engine: 引擎名称 (mock, azure, aliyun, tencent)
            api_key: API密钥
            region: 服务区域
            **kwargs: 其他配置参数
            
        Returns:
            TTSProvider实例
        """
        provider_class = cls._providers.get(engine.lower())
        if not provider_class:
            raise ValueError(
                f"不支持的TTS引擎: {engine}. "
                f"可用引擎: {', '.join(cls._providers.keys())}"
            )
        
        return provider_class(api_key=api_key, region=region, **kwargs)
    
    @classmethod
    def get_available_engines(cls) -> list:
        """获取所有可用的TTS引擎"""
        return list(cls._providers.keys())

