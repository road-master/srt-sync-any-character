from pathlib import Path
import subprocess


def get_duration(file_make_zero: Path) -> float:
    """Check duration of video file.

    - Answer: ffmpeg - How to get video duration in seconds? - Super User
      https://superuser.com/a/945604/1167741
    """
    args = [
        "-show_entries",
        "format=duration",
        "-output_format",
        "default=noprint_wrappers=1:nokey=1",
        "-loglevel",
        "repeat+fatal",
    ]
    command = ["ffprobe", *args, str(file_make_zero)]
    # Reason: Confirmed that command isn't so risky.
    completed_process = subprocess.run(command, text=True, capture_output=True, check=True)  # noqa: S603
    return float(completed_process.stdout)
