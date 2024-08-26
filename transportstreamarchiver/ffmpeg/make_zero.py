from pathlib import Path

from transportstreamarchiver.ffmpeg.execution import execute_ffmpeg
from transportstreamarchiver.ffmpeg.seek_range import SeekRange


def make_zero(file_input: Path, seek_range: SeekRange) -> Path:
    """Make the first timestamp of the video zero.

    Note that video and audio streams don't seem to start with zero
    due to the data stream seems to be always zero.
        ffprobe -pretty -v error -select_streams d:0 -show_entries stream=start_pts,start_time \
        <file.ts>
        [PROGRAM]
        [STREAM]
        start_pts=0
        start_time=0:00:00.000000
        [/STREAM]
        [/PROGRAM]
        [STREAM]
        start_pts=0
        start_time=0:00:00.000000
        [/STREAM]
    Args:
        file_input (Path): Path to the input video file.
    """
    file_make_zero = file_input.parent / Path(f"{file_input.stem}_make_zero.ts")
    if file_make_zero.exists():
        return file_make_zero
    parameters = []
    if seek_range.ss is not None:
        parameters.extend(["-ss", f"{seek_range.ss}"])
    if seek_range.to is not None:
        parameters.extend(["-to", f"{seek_range.to}"])
    parameters.extend(
        [
            "-copyts",
            "-start_at_zero",
            "-avoid_negative_ts",
            "make_zero",
            "-i",
            str(file_input),
            "-map",
            "0",
            "-c",
            "copy",
            "-muxpreload",
            "0",
            "-muxdelay",
            "0",
            "-y",
            str(file_make_zero),
        ],
    )
    execute_ffmpeg(parameters, "Failed to make zero", file_make_zero)
    return file_make_zero
