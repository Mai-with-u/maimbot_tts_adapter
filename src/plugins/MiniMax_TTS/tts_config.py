from dataclasses import dataclass
from typing import Dict, Any
import toml


@dataclass
class MiniMaxAppConfig:
    t2a_url: str
    api_key: str
    model: str
    language_boost: str


@dataclass
class MiniMaxVoiceConfig:
    voice_id: str
    speed: float
    vol: float
    pitch: int


@dataclass
class MiniMaxAudioConfig:
    sample_rate: int
    bitrate: int
    format: str
    channel: int


@dataclass
class MiniMaxTTSConfig:
    app: MiniMaxAppConfig
    voice: MiniMaxVoiceConfig
    audio: MiniMaxAudioConfig

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MiniMaxTTSConfig":
        app_data = data.get("app", {})
        voice_data = data.get("voice", {})
        audio_data = data.get("audio", {})
        return cls(
            app=MiniMaxAppConfig(**app_data),
            voice=MiniMaxVoiceConfig(**voice_data),
            audio=MiniMaxAudioConfig(**audio_data),
        )


class MiniMaxTTSBaseConfig:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config_data = load_tts_config(config_path)
        self.tts_config: MiniMaxTTSConfig = MiniMaxTTSConfig.from_dict(self.config_data)
        self.app: MiniMaxAppConfig = self.tts_config.app
        self.voice: MiniMaxVoiceConfig = self.tts_config.voice
        self.audio: MiniMaxAudioConfig = self.tts_config.audio

    def __getitem__(self, key: str) -> Any:
        return self.config_data[key]

    def __setitem__(self, key: str, value: Any):
        self.config_data[key] = value

    def __repr__(self) -> str:
        return str(self.config_data)


def load_tts_config(config_path: str) -> Dict[str, Any]:
    """加载TOML配置文件

    Args:
        config_path (str): 配置文件路径

    Returns:
        config (Dict[str, Any]): 配置文件内容
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = toml.load(f)
    return config
