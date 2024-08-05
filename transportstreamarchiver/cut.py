from pathlib import Path
from typing import Optional

from transportstreamarchiver import ffmpeg, ffprobe
from transportstreamarchiver.ffmpeg.seek_range.factory import SeekRangeFactory


def cut(
    file_input: Path,
    file_output: Path,
    *,
    string_from: Optional[str] = None,
    string_to: Optional[str] = None,
) -> None:
    ffmpeg_seek_range = SeekRangeFactory.create(file_input, string_from=string_from, string_to=string_to)
    ffmpeg.cut(file_input, ffmpeg_seek_range, file_output)
    ffprobe.is_cut_by_key_frame(file_output)
