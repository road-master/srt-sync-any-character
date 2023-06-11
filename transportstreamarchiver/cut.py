from pathlib import Path
from typing import Optional
from transportstreamarchiver import ffmpeg
from transportstreamarchiver import ffprobe
from transportstreamarchiver.mpv.offset import OffsetChecker


def cut(
    file_input: Path,
    file_output: Path,
    *,
    string_from: Optional[str] = None,
    string_to: Optional[str] = None,
) -> None:
    offset = OffsetChecker(file_input).offset
    ffmpeg.cut(file_input, offset, file_output, string_from=string_from, string_to=string_to)
    ffprobe.is_cut_by_key_frame(file_output)
