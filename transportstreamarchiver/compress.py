from pathlib import Path
from typing import Optional
from transportstreamarchiver import ffmpeg
from transportstreamarchiver.mpv.offset import OffsetChecker


def compress(
    file_input: Path,
    file_output: Path,
    *,
    string_from: Optional[str] = None,
    string_to: Optional[str] = None,
) -> None:
    offset = OffsetChecker(file_input).offset
    ffmpeg.compress(file_input, offset, file_output, string_from=string_from, string_to=string_to)
