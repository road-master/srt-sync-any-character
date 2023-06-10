from pathlib import Path
from transportstreamarchiver import ffmpeg
from transportstreamarchiver import ffprobe
from transportstreamarchiver.mpv.offset import OffsetChecker


def cut(
    file_input: Path,
    string_from: str,
    string_to: str,
    file_output: Path,
) -> None:
    offset = OffsetChecker(file_input).offset
    ffmpeg.cut(file_input, offset, string_from, string_to, file_output)
    ffprobe.is_cut_by_key_frame(file_output)
