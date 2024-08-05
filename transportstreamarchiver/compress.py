from pathlib import Path
from typing import Optional

from transportstreamarchiver import ffmpeg
from transportstreamarchiver.ffmpeg.seek_range.factory import SeekRangeFactory


def compress(
    file_input: Path,
    file_output: Path,
    *,
    string_from: Optional[str] = None,
    string_to: Optional[str] = None,
) -> None:
    ffmpeg_seek_range = SeekRangeFactory.create(file_input, string_from=string_from, string_to=string_to)
    ffmpeg.compress(file_input, ffmpeg_seek_range, file_output)
