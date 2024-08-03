import subprocess
import sys
from pathlib import Path


def make_zero(file_input: Path) -> None:
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
    return_code = subprocess.call(
        [
            "ffmpeg",
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
        ]
    )


if __name__ == "__main__":
    file_input = Path(sys.argv[1])
    make_zero(file_input)
