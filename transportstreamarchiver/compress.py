from pathlib import Path
from typing import Optional

from transportstreamarchiver import ffmpeg
from transportstreamarchiver.ffmpeg.date_format import SeekRange


def compress(
    file_input: Path,
    file_output: Path,
    *,
    string_from: Optional[str] = None,
    string_to: Optional[str] = None,
) -> None:
    ffmpeg_seek_range = SeekRange(file_input, string_from=string_from, string_to=string_to)
    ffmpeg.compress(file_input, ffmpeg_seek_range, file_output)
