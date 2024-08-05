from logging import getLogger

# Reason: Using subprocess is necessary to call FFmpeg.
from pathlib import Path
import subprocess  # nosec: B404

from transportstreamarchiver.ffmpeg.exceptions import FFmpegProcessError


def execute_ffmpeg(parameters: list[str], error_message: str, file_output: Path) -> None:
    command = ["ffmpeg"]
    command.extend(parameters)
    logger = getLogger(__name__)
    logger.debug(" ".join(command))
    # Reason: Confirmed that command isn't so risky.
    return_code = subprocess.call(command)  # noqa: S603  # nosec: S607
    if return_code != 0 or not file_output.exists():
        raise FFmpegProcessError(error_message)
