"""AI Story Commerce — FFmpeg 后期处理接口

封装 FFmpeg 的视频后期处理功能，包括：
- 视频合并
- 音频合成
- 字幕添加
- 视频转码
- 视频剪辑
"""

import os
import subprocess
import hashlib
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FFmpegResult:
    """FFmpeg 处理结果"""
    success: bool
    output_path: Optional[str] = None
    sha256: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    command: Optional[str] = None


class FFmpegProcessor:
    """FFmpeg 后期处理器"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path

    def check_available(self) -> bool:
        """检查 FFmpeg 是否可用"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def merge_video_audio(self, video_path: str, audio_path: str,
                          output_path: str) -> FFmpegResult:
        """将视频和音频合并"""
        if not os.path.exists(video_path):
            return FFmpegResult(success=False, error_message=f"视频文件不存在: {video_path}")
        if not os.path.exists(audio_path):
            return FFmpegResult(success=False, error_message=f"音频文件不存在: {audio_path}")

        cmd = [
            self.ffmpeg_path, "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path,
        ]
        return self._run_ffmpeg(cmd, output_path)

    def concat_videos(self, video_paths: List[str], output_path: str) -> FFmpegResult:
        """合并多个视频文件"""
        for v in video_paths:
            if not os.path.exists(v):
                return FFmpegResult(success=False, error_message=f"视频文件不存在: {v}")

        # 创建文件列表
        list_path = output_path + ".txt"
        with open(list_path, "w") as f:
            for v in video_paths:
                f.write(f"file '{v}'\n")

        cmd = [
            self.ffmpeg_path, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_path,
            "-c", "copy",
            output_path,
        ]
        result = self._run_ffmpeg(cmd, output_path)
        # 清理临时文件
        try:
            os.unlink(list_path)
        except OSError:
            pass
        return result

    def add_subtitles(self, video_path: str, subtitle_path: str,
                      output_path: str) -> FFmpegResult:
        """为视频添加字幕"""
        if not os.path.exists(video_path):
            return FFmpegResult(success=False, error_message=f"视频文件不存在: {video_path}")
        if not os.path.exists(subtitle_path):
            return FFmpegResult(success=False, error_message=f"字幕文件不存在: {subtitle_path}")

        cmd = [
            self.ffmpeg_path, "-y",
            "-i", video_path,
            "-vf", f"subtitles={subtitle_path}",
            "-c:a", "copy",
            output_path,
        ]
        return self._run_ffmpeg(cmd, output_path)

    def trim_video(self, video_path: str, start_time: float,
                   end_time: float, output_path: str) -> FFmpegResult:
        """剪辑视频片段"""
        if not os.path.exists(video_path):
            return FFmpegResult(success=False, error_message=f"视频文件不存在: {video_path}")

        duration = end_time - start_time
        cmd = [
            self.ffmpeg_path, "-y",
            "-ss", str(start_time),
            "-i", video_path,
            "-t", str(duration),
            "-c", "copy",
            output_path,
        ]
        return self._run_ffmpeg(cmd, output_path)

    def convert_format(self, input_path: str, output_path: str,
                       format_name: str = "mp4") -> FFmpegResult:
        """转换视频格式"""
        if not os.path.exists(input_path):
            return FFmpegResult(success=False, error_message=f"输入文件不存在: {input_path}")

        cmd = [
            self.ffmpeg_path, "-y",
            "-i", input_path,
            "-f", format_name,
            output_path,
        ]
        return self._run_ffmpeg(cmd, output_path)

    def get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """获取视频信息（使用 ffprobe）"""
        ffprobe_path = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
        if not os.path.exists(video_path):
            return None

        try:
            result = subprocess.run(
                [
                    ffprobe_path, "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    video_path,
                ],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            pass
        return None

    def _run_ffmpeg(self, cmd: List[str], output_path: str) -> FFmpegResult:
        """运行 FFmpeg 命令"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=300,
            )
            command_str = " ".join(cmd)

            if result.returncode != 0:
                return FFmpegResult(
                    success=False,
                    error_message=result.stderr or "FFmpeg 执行失败",
                    command=command_str,
                )

            if not os.path.exists(output_path):
                return FFmpegResult(
                    success=False,
                    error_message="输出文件未生成",
                    command=command_str,
                )

            # 计算 SHA256
            sha256 = hashlib.sha256()
            with open(output_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)

            # 获取时长
            info = self.get_video_info(output_path)
            duration = None
            if info and "format" in info:
                try:
                    duration = float(info["format"].get("duration", 0))
                except (ValueError, TypeError):
                    pass

            return FFmpegResult(
                success=True,
                output_path=output_path,
                sha256=sha256.hexdigest(),
                duration_seconds=duration,
                command=command_str,
            )
        except subprocess.TimeoutExpired:
            return FFmpegResult(
                success=False,
                error_message="FFmpeg 执行超时",
                command=" ".join(cmd),
            )
        except Exception as e:
            return FFmpegResult(
                success=False,
                error_message=str(e),
                command=" ".join(cmd),
            )


__all__ = ["FFmpegProcessor", "FFmpegResult"]
