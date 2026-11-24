"""AI Story Commerce — 视频生产适配器接口

定义图像生成、视频生成、配音生成的适配器基类。
禁止与单一模型硬耦合，所有生成平台均通过适配器接入。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
import hashlib
import os


def compute_sha256(file_path: str) -> str:
    """计算文件 SHA256 哈希值"""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class GenerationResult:
    """生成结果"""
    success: bool
    file_path: Optional[str] = None
    sha256: Optional[str] = None
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class ImageGenerationAdapter(ABC):
    """图像生成适配器基类"""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> GenerationResult:
        """根据提示词生成图像"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """返回模型名称"""
        pass


class VideoGenerationAdapter(ABC):
    """视频生成适配器基类"""

    @abstractmethod
    def generate(self, prompt: str, image_path: Optional[str] = None,
                 duration_seconds: float = 5.0, **kwargs) -> GenerationResult:
        """根据提示词生成视频"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """返回模型名称"""
        pass


class VoiceGenerationAdapter(ABC):
    """配音生成适配器基类"""

    @abstractmethod
    def generate(self, text: str, voice_reference: Optional[str] = None,
                 **kwargs) -> GenerationResult:
        """根据文本生成音频"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """返回模型名称"""
        pass


class MockImageAdapter(ImageGenerationAdapter):
    """Mock 图像生成适配器（用于开发和测试，不调用真实模型）"""

    def __init__(self, output_dir: str = "data/mock_outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, prompt: str, **kwargs) -> GenerationResult:
        h = hashlib.sha256(prompt.encode()).hexdigest()[:12]
        file_path = os.path.join(self.output_dir, f"mock_image_{h}.png")
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(b"mock image placeholder")
        return GenerationResult(
            success=True,
            file_path=file_path,
            sha256=compute_sha256(file_path),
            file_size_bytes=os.path.getsize(file_path),
            width=1024,
            height=1024,
            raw_response={"model": "mock", "prompt": prompt},
        )

    def get_model_name(self) -> str:
        return "mock-image-v1"


class MockVideoAdapter(VideoGenerationAdapter):
    """Mock 视频生成适配器"""

    def __init__(self, output_dir: str = "data/mock_outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, prompt: str, image_path: Optional[str] = None,
                 duration_seconds: float = 5.0, **kwargs) -> GenerationResult:
        h = hashlib.sha256((prompt + str(duration_seconds)).encode()).hexdigest()[:12]
        file_path = os.path.join(self.output_dir, f"mock_video_{h}.mp4")
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(b"mock video placeholder")
        return GenerationResult(
            success=True,
            file_path=file_path,
            sha256=compute_sha256(file_path),
            file_size_bytes=os.path.getsize(file_path),
            duration_seconds=duration_seconds,
            width=1080,
            height=1920,
            raw_response={"model": "mock", "prompt": prompt, "duration": duration_seconds},
        )

    def get_model_name(self) -> str:
        return "mock-video-v1"


class MockVoiceAdapter(VoiceGenerationAdapter):
    """Mock 配音生成适配器"""

    def __init__(self, output_dir: str = "data/mock_outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, text: str, voice_reference: Optional[str] = None,
                 **kwargs) -> GenerationResult:
        h = hashlib.sha256((text + str(voice_reference)).encode()).hexdigest()[:12]
        file_path = os.path.join(self.output_dir, f"mock_voice_{h}.mp3")
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(b"mock audio placeholder")
        return GenerationResult(
            success=True,
            file_path=file_path,
            sha256=compute_sha256(file_path),
            file_size_bytes=os.path.getsize(file_path),
            duration_seconds=5.0,
            raw_response={"model": "mock", "text": text, "voice": voice_reference},
        )

    def get_model_name(self) -> str:
        return "mock-voice-v1"
