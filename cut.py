from pathlib import Path
import sys
import subprocess

from ffmpeg_date_format import FFmpegSeekRange
from key_frame import is_cut_by_key_frame


ffmpeg_seek_range = FFmpegSeekRange(sys.argv[1], sys.argv[2], sys.argv[3])
file_input = Path("original.ts")
file_output = Path(sys.argv[4])

return_code = subprocess.call(
    [
        "ffmpeg",
        "-ss",
        f'{ffmpeg_seek_range.ss}',
        "-to",
        f'{ffmpeg_seek_range.to}',
        "-i",
        str(file_input),
        "-map",
        "0",
        "-c",
        "copy",
        "-async",
        "1",
        "-strict",
        "-2",
        "-avoid_negative_ts",
        "1",
        "-y",
        str(file_output),
    ]
)
if not file_output.exists():
    raise Exception("Faild to cut")
if not is_cut_by_key_frame(file_output):
    raise Exception("Faild to cut by key frame")
