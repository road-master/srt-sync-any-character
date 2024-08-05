from bisect import bisect_left
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path
import re

# Reason: Using subprocess is necessary to call FFprobe.
import subprocess  # nosec: B404

from transportstreamarchiver.ffprobe.exceptions import FFprobeProcessError

__all__ = ["is_cut_by_key_frame"]

logger = getLogger(__name__)


def process_open(file_make_zero: Path, *, only_head: bool = False) -> subprocess.Popen[str]:
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
    logger.debug(" ".join(command))
    # Reason: Confirmed that command isn't so risky.
    return subprocess.Popen(  # noqa: S603  # nosec: B603
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def create_list_is_key_frame(file: Path) -> list[bool]:
    list_is_key_frame: list[bool] = []
    process = process_open(file, only_head=True)
    while process.poll() is None:
        # Reason: The condition `process.poll() is None` guarantees that `process.stdout` is not None.
        line: str = process.stdout.readline()  # type: ignore[union-attr]
        stripped_line = line.strip()
        split_line = line.split(",")
        # May ['\r'] in case when .ts renamed from .m2ts
        if len(split_line) <= 1 or split_line[1] == "N/A":
            continue
        list_is_key_frame.append(bool(re.search(",K", stripped_line)))
    return list_is_key_frame


def is_cut_by_key_frame(file: Path) -> None:
    list_is_key_frame = create_list_is_key_frame(file)
    if not list_is_key_frame[0]:
        msg = "First frame is not key frame"
        raise FFprobeProcessError(msg)
    for i in range(1, 15):
        if list_is_key_frame[i]:
            msg = "Interval between key frames is not 14 frames"
            raise FFprobeProcessError(msg)
    if not list_is_key_frame[15]:
        msg = "Interval between key frames is not 14 frames"
        raise FFprobeProcessError(msg)


def get_list_key_frame(file_make_zero: Path) -> list[timedelta]:
    list_key_frame: list[timedelta] = []
    process = process_open(file_make_zero)
    while process.poll() is None:
        # Reason: The condition `process.poll() is None` guarantees that `process.stdout` is not None.
        line: str = process.stdout.readline()  # type: ignore[union-attr]
        stripped_line = line.strip()
        split_line = stripped_line.split(",")
        # May ['\r'] in case when .ts renamed from .m2ts
        if len(split_line) <= 1 or split_line[1] == "N/A":
            continue
        pts_time = split_line[1]
        if re.search(",K", stripped_line):
            split_pts_time = pts_time.split(".")
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
        # Reason: The condition `process.poll() is None` guarantees that `process.stdout` is not None.
        line: str = process.stdout.readline()  # type: ignore[union-attr]
        stripped_line = line.strip()
        split_line = stripped_line.split(",")
        # May ['\r'] in case when .ts renamed from .m2ts
        if len(split_line) <= 1 or split_line[1] == "N/A":
            continue
        pts_time = split_line[1]
        # if re.search(',K', line):
        split_pts_time = pts_time.split(".")
        list_frame.append(
            PresentationTimeStamp(
                time=timedelta(seconds=int(split_pts_time[0]), microseconds=int(split_pts_time[1])),
                is_key="K__" if re.search(",K", stripped_line) else "___",
            ),
        )
    return list_frame


def get_delta_accurate(delta: timedelta, list_key_frame: list[datetime]) -> list[str]:
    delta_bisect_left = bisect_left(list_key_frame, delta)
    return [
        str(list_key_frame[delta_bisect_left - 1]),
        str(list_key_frame[delta_bisect_left]),
        str(list_key_frame[delta_bisect_left + 1]),
    ]
