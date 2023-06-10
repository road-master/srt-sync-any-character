from pathlib import Path
import subprocess
import sys


def make_zero(file_input: Path) -> None:
    """Make the first timestamp of the video zero.

    Args:
        file_input (Path): Path to the input video file.
    """
    file_make_zero = Path(f"{file_input.stem}_make_zero.ts")
    return_code = subprocess.call(
        [
            "ffmpeg",
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
            "-avoid_negative_ts",
            "make_zero",
            "-y",
            str(file_make_zero),
        ]
    )


if __name__ == "__main__":
    file_input = Path(sys.argv[1])
    make_zero(file_input)
