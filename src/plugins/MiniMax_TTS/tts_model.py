import aiohttp
from pathlib import Path
from src.plugins.base_tts_model import BaseTTSModel
from .tts_config import MiniMaxTTSBaseConfig


class TTSModel(BaseTTSModel):
    def __init__(self):
        """初始化TTS模型"""
        self.config = self.load_config()

    def load_config(self) -> "MiniMaxTTSBaseConfig":
        """加载配置文件"""
        config_path = Path(__file__).parent.parent.parent.parent / "configs" / "MiniMax_tts.toml"
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        return MiniMaxTTSBaseConfig(str(config_path))

    async def tts(self, text: str, **kwargs) -> bytes:
        """
        文本转语音
        Args:
            text (str): 合成内容
        Returns:
            音频二进制数据流(wav格式)
        """
        print(f"开始调用MiniMax TTS API生成音频，文本: {text[:30]}{'...' if len(text) > 30 else ''}")
        if not self.config.app.api_key:
            raise RuntimeError("MiniMax TTS api_key 为空，请在 configs/MiniMax_tts.toml 中填写")
        headers = {
            "Authorization": f"Bearer {self.config.app.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.config.app.model,
            "text": text,
            "stream": False,
            "output_format": "hex",
            "voice_setting": {
                "voice_id": self.config.voice.voice_id,
                "speed": self.config.voice.speed,
                "vol": self.config.voice.vol,
                "pitch": self.config.voice.pitch,
            },
            "audio_setting": {
                "sample_rate": self.config.audio.sample_rate,
                "bitrate": self.config.audio.bitrate,
                "format": self.config.audio.format,
                "channel": self.config.audio.channel,
            },
        }
        if self.config.app.language_boost:
            payload["language_boost"] = self.config.app.language_boost
        async with aiohttp.ClientSession() as session:
            async with session.post(self.config.app.t2a_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    detail = (await response.text())[:300]
                    raise RuntimeError(f"MiniMax TTS API请求失败，状态码: {response.status}，响应: {detail}")
                resp_json = await response.json()
                base_resp = resp_json.get("base_resp") or {}
                if base_resp.get("status_code") != 0:
                    status_msg = base_resp.get("status_msg") or base_resp.get("status_code")
                    raise RuntimeError(f"MiniMax TTS请求失败: {status_msg}")
                audio_hex = (resp_json.get("data") or {}).get("audio")
                if not audio_hex:
                    raise RuntimeError("MiniMax TTS API未返回音频数据")
                try:
                    return bytes.fromhex(audio_hex)
                except ValueError as exc:
                    raise RuntimeError("MiniMax TTS 返回的 data.audio 不是 hex 编码") from exc

    async def tts_stream(self, text: str, **kwargs):
        """
        文本转语音，流式方式（本插件未实现）
        """
        raise RuntimeError("MiniMax TTS 插件不支持流式方式，请将 stream_mode 设为 false")
