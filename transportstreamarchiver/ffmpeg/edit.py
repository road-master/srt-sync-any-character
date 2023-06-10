from datetime import timedelta
from pathlib import Path
import sys
import subprocess
from typing import Union

from transportstreamarchiver.ffmpeg import SeekRange
from transportstreamarchiver.ffmpeg.exceptions import FFmpegProcessError


__all__ = ["cut", "export_subtitle", "import_subtitle"]


def cut(
    file_input: Path,
    offset: Union[timedelta, str],
    string_from: str,
    string_to: str,
    file_output: Path
) -> None:
    ffmpeg_seek_range = SeekRange(offset, string_from, string_to)
    return_code = subprocess.call(
        [
            "ffmpeg",
            "-ss",
            f'{ffmpeg_seek_range.ss}',
            "-to",
            f'{ffmpeg_seek_range.to}',
            "-i",
            str(file_input),
            "-map",
            "0",
            "-c",
            "copy",
            "-async",
            "1",
            "-strict",
            "-2",
            "-avoid_negative_ts",
            "1",
            "-y",
            str(file_output),
        ]
    )
    if return_code != 0 or not file_output.exists():
        raise FFmpegProcessError("Failed to cut")


def export_subtitle(file_input: Path, file_output: Path) -> None:
    return_code = subprocess.call(
        [
            "ffmpeg",
            "-fix_sub_duration",
            "-i",
            str(file_input),
            "-c:s",
            "text",
            "-y",
            str(file_output),
        ]
    )
    if return_code != 0 or not file_output.exists():
        raise FFmpegProcessError("Failed to export subtitle")


def import_subtitle(ts: Path, subtitle: Path, output: Path) -> None:
    return_code = subprocess.call(
        [
            "ffmpeg",
            "-i",
            str(ts),
            "-i",
            str(subtitle),
            "-c",
            "copy",
            "-c:s",
            "mov_text",
            "-metadata:s:s:0",
            "language=jpn",
            "-y",
            str(output),
        ]
    )
    if return_code != 0 or not output.exists():
        raise FFmpegProcessError("Failed to import subtitle")
