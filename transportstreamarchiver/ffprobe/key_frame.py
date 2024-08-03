import re
import subprocess
import sys
from bisect import bisect_left
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from transportstreamarchiver.ffprobe.exceptions import FFprobeProcessError

__all__ = ["is_cut_by_key_frame"]


def process_open(file_make_zero: Path, only_head: bool = None) -> subprocess.Popen:
    args = [
            "-hide_banner",
            "-select_streams",
            "v",
            "-show_entries",
            "packet=pts_time,flags",
            "-of",
            "csv",
    ]
    if only_head:
        args.append("-read_intervals")
        args.append("%+#16")
    command = ["ffprobe", *args, str(file_make_zero)]
    print(' '.join(command))
    return subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def is_cut_by_key_frame(file: Path) -> None:
    list_is_key_frame: list[bool] = []
    process = process_open(file, only_head=True)
    while process.poll() is None:
        line = process.stdout.readline().strip()
        print(line)
        split_line = line.split(',')
        # May ['\r'] in case when .ts renamed from .m2ts
        if len(split_line) <= 1 or split_line[1] == 'N/A':
            continue
        list_is_key_frame.append(re.search(',K', line))
    if not list_is_key_frame[0]:
        raise FFprobeProcessError("First frame is not key frame")
    for i in range(1, 15):
        if list_is_key_frame[i]:
            raise FFprobeProcessError("Interval between key frames is not 14 frames")
    if not list_is_key_frame[15]:
        raise FFprobeProcessError("Interval between key frames is not 14 frames")


def get_list_key_frame(file_make_zero: Path) -> list[datetime]:
    list_key_frame: list[datetime] = []
    process = process_open(file_make_zero)
    while process.poll() is None:
        line = process.stdout.readline().strip()
        split_line = line.split(',')
        # May ['\r'] in case when .ts renamed from .m2ts
        if len(split_line) <= 1 or split_line[1] == 'N/A':
            continue
        pts_time = split_line[1]
        if re.search(',K', line):
            split_pts_time = pts_time.split('.')
            list_key_frame.append(timedelta(seconds=int(split_pts_time[0]), microseconds=int(split_pts_time[1])))
    return list_key_frame


@dataclass
class PresentationTimeStamp:
    time: timedelta
    is_key: str


def inspect_frame(file_make_zero: Path) -> list[PresentationTimeStamp]:
    list_frame: list[PresentationTimeStamp] = []
    process = process_open(file_make_zero)
    while process.poll() is None:
        line = process.stdout.readline().strip()
        split_line = line.split(',')
        # May ['\r'] in case when .ts renamed from .m2ts
        if len(split_line) <= 1 or split_line[1] == 'N/A':
            continue
        pts_time = split_line[1]
        # if re.search(',K', line):
        split_pts_time = pts_time.split('.')
        list_frame.append(
            PresentationTimeStamp(
                time=timedelta(seconds=int(split_pts_time[0]), microseconds=int(split_pts_time[1])),
                is_key="K__" if re.search(',K', line) else "___",
            )
        )
    return list_frame


def print_frame(file_make_zero: Path) -> list[datetime]:
    for index, frame in enumerate(inspect_frame(file_make_zero)):
        print(f"{index}: {frame['time']}, {frame['is_key']}")


def get_delta_accurate(delta: timedelta, list_key_frame: list[datetime]) -> list[str]:
    delta_bisect_left = bisect_left(list_key_frame, delta)
    return [
        str(list_key_frame[delta_bisect_left - 1]),
        str(list_key_frame[delta_bisect_left]),
        str(list_key_frame[delta_bisect_left + 1]),
    ]


if __name__ == "__main__":
    file_make_zero = Path(sys.argv[1])
    # ffmpeg_seek_range = SeekRange(sys.argv[2], sys.argv[3], sys.argv[4])
    list_key_frame = get_list_key_frame(file_make_zero)
    print(list_key_frame)
    # delta_accurate_from = get_delta_accurate(ffmpeg_seek_range.ss, list_key_frame)
    # delta_accurate_to = get_delta_accurate(ffmpeg_seek_range.to, list_key_frame)
