from bisect import bisect_left
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging import DEBUG, getLogger, INFO
from pathlib import Path
import re

# Reason: Using subprocess is necessary to call FFprobe.
import subprocess
from typing import Generic, TypeVar  # nosec: B404

from transportstreamarchiver.ffprobe.duration import get_duration
from transportstreamarchiver.ffprobe.exceptions import FFprobeProcessError, SkipFrame

__all__ = ["is_cut_by_key_frame_at_start", "is_cut_by_key_frame_at_end"]

logger = getLogger(__name__)


def process_open(
    file_make_zero: Path,
    *,
    only_head: bool | None = None,
    entries: str | None = None,
) -> subprocess.Popen[str]:
    """Run FFprobe process.

    Args:
        file_make_zero: File path.
        only_head: If True, read only the first 16 frames.
    """
    args = [
        "-hide_banner",
        "-select_streams",
        "v",
        "-show_entries",
        entries if entries else "packet=pts_time,flags",
        "-output_format",
        "csv",
    ]
    if only_head is True:
        args.append("-read_intervals")
        args.append("%+#16")
    elif only_head is False:
        duration = get_duration(file_make_zero) - 0.7
        args.append("-read_intervals")
        args.append(str(duration))
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


T = TypeVar("T")


class Inspector(Generic[T]):
    def __init__(
        self,
        inspect_line: Callable[[str], T],
        *,
        log_level: int = DEBUG,
        entries: str | None = None,
    ) -> None:
        self.logger = getLogger(__name__)
        self.inspect_line = inspect_line
        self.log_level = log_level
        self.entries = entries
        self.list_something: list[T] = []

    def inspect(self, file_make_zero: Path, *, only_head: bool | None = None) -> list[T]:
        with process_open(file_make_zero, only_head=only_head, entries=self.entries) as process:
            while process.poll() is None:
                # Reason: The condition `process.poll() is None` guarantees that `process.stdout` is not None.
                line: str = process.stdout.readline()  # type: ignore[union-attr]
                stripped_line = line.strip()
                logger.log(self.log_level, stripped_line)
                try:
                    something = self.inspect_line(stripped_line)
                except SkipFrame:
                    continue
                self.list_something.append(something)
        return self.list_something


def create_list_key_frame(file_make_zero: Path) -> list[str]:
    def inspect_key_frame(stripped_line: str) -> str:
        split_line = stripped_line.split(",")
        # May ['\r'] in case when .ts renamed from .m2ts
        if len(split_line) <= 1 or split_line[1] == "N/A":
            raise SkipFrame
        if re.search(",K", stripped_line):
            return stripped_line.split(",")[1]
        raise SkipFrame

    return Inspector(inspect_key_frame).inspect(file_make_zero)


def inspect_is_key_frame(stripped_line: str) -> tuple[str, bool]:
    split_line = stripped_line.split(",")
    try:
        pts_time = split_line[1]
    except IndexError:
        raise SkipFrame
    is_key_frame = split_line[2] == "K__"
    return (pts_time, is_key_frame)


def reorganize_key_frame(list_line: list[list[str]]) -> dict[str, list[str]]:
    dictionary_frame: dict[str, list[str]] = {}
    try:
        for each_line in list_line:
            print(each_line)
            # kind = each_line[0]
            pts_time = each_line[1]
            if pts_time in dictionary_frame:
                dictionary_frame[each_line[1]].append(each_line[2])
            else:
                dictionary_frame[each_line[1]] = [each_line[2]]
            # if kind == "packet":
            # elif kind == "frame":
            #     dictionary_frame[each_line[1]] = [each_line[2]]
            # else:
            #     raise ValueError(f"Unknown kind: {kind}")
    except IndexError:
        logger.exception("IndexError")
        pass
    for key, value in dictionary_frame.items():
        print(key, value)
    return dictionary_frame


ENTRIES_PACKET_AND_FRAME = "packet=pts_time,flags:frame=pts_time,pict_type"


def is_cut_by_key_frame_at_start(file: Path) -> None:
    inspector = Inspector(inspect_is_key_frame, log_level=INFO)
    list_is_key_frame = inspector.inspect(file, only_head=True)
    if not list_is_key_frame[0][1]:
        msg = "First frame is not key frame"
        raise FFprobeProcessError(msg)
    for index in range(1, 15):
        if list_is_key_frame[index][1]:
            msg = "Interval between key frames is not 14 frames"
            raise FFprobeProcessError(msg)
    if not list_is_key_frame[15][1]:
        msg = "Interval between key frames is not 14 frames"
        raise FFprobeProcessError(msg)


def is_cut_by_key_frame_at_end(file: Path) -> None:
    inspector = Inspector(inspect_is_key_frame, log_level=INFO)
    list_is_key_frame = inspector.inspect(file, only_head=False)
    for index_last_key_frame in range(1, 15):
        if list_is_key_frame[-index_last_key_frame][1]:
            break
    else:
        msg = "Key frame is not found in last 15 frames"
        raise FFprobeProcessError(msg)
    for index in range(1, index_last_key_frame):
        if list_is_key_frame[-(index)][0] > list_is_key_frame[-index_last_key_frame][0]:
            msg = "The PTS time of following frame after last key frame is later than last key frame"
            raise FFprobeProcessError(msg)
    for index in range(1, 15):
        if list_is_key_frame[-(index + index_last_key_frame)][1]:
            msg = "Interval between key frames is not 14 frames"
            raise FFprobeProcessError(msg)
    if not list_is_key_frame[-(15 + index_last_key_frame)][1]:
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
