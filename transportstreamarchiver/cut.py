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
    file_input = Path("original.ts")
    offset = OffsetChecker(file_input).offset
    ffmpeg.cut(file_input, offset, string_from, string_to, file_output)
    if not ffprobe.is_cut_by_key_frame(file_output):
        raise Exception("Failed to cut by key frame")
