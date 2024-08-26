from collections.abc import Generator, Iterable
from dataclasses import dataclass
import json
from logging import basicConfig, INFO
from pathlib import Path
import subprocess
import sys

from transportstreamarchiver.ffmpeg.edit import cut
from transportstreamarchiver.ffmpeg.make_zero import make_zero
from transportstreamarchiver import ffprobe
from transportstreamarchiver.ffprobe.key_frame import create_list_key_frame


def generateCommand(index: list[int], list_time: list[str]) -> str:
    text = ""
    for i, ii in enumerate(index):
        file_name = f"output/output{i}.mp4"
        delta = list_time[ii + 1] - list_time[ii]
        cmd = f"ffmpeg -ss {list_time[ii]} -i billiards.mp4 -t {delta} {file_name}"
        print(cmd)
        subprocess.call(cmd, shell=True)
        text += f"file {file_name}\n"
    return text


@dataclass
class ConsecutivePeriod:
    ss: int
    to: int


def create_list_consecutive_period(list_index: list[int]) -> Generator[ConsecutivePeriod, None, None]:
    if not list_index:
        return
    start_index = list_index[0]
    try:
        for key, index in enumerate(list_index):
            if list_index[key + 1] - index == 1:
                continue
            yield ConsecutivePeriod(start_index, index)
            start_index = list_index[key + 1]
    except IndexError:
        yield ConsecutivePeriod(start_index, index)


@dataclass
class SeekRange:
    ss: str
    to: str

    def __str__(self) -> str:
        return f"{self.to_string(self.ss)} to {self.to_string(self.to)}"

    @staticmethod
    def to_string(string_second: str) -> str:
        """Convert second to HH:MM:SS.mmm format."""
        # The `//` operator is used instead of `/` to get an integer.
        # The `%` operator is used to get the remainder.
        second = float(string_second)
        hour = second // 3600
        minute = (second % 3600) // 60
        second = (second % 3600) % 60
        return f"{int(hour):02}:{int(minute):02}:{int(second):02}.{int((second - int(second)) * 1000):03}"


def create_list_period(
    list_consecutive_period: Iterable[ConsecutivePeriod],
    list_time: list[str],
) -> Generator[SeekRange, None, None]:
    for period in list_consecutive_period:
        print(period)
        # Why +2:
        # Because, at least video has to include until the start of next scene.
        # And, when just only take next scene, FFmpeg would take the key frame before the start of next scene.
        yield SeekRange(list_time[period.ss], list_time[period.to + 1])


class Frames:
    # The gap between the FFprobe's PTS_TIME and FFmpeg's -ss option position.
    # Because, FFmpeg would take the key frame before the end of the scene.
    # Following value is based on experience in research with actual video.
    INDEX_GAP_BETWEEN_FFPROBE_AND_FFMPEG = 3

    def __init__(self, file_make_zero: Path) -> None:
        self.file_make_zero = file_make_zero
        self.list_frame = create_list_key_frame(file_make_zero)
        print(self.list_frame)

    def search_outside_neighbor_frame(self, seek_ranges: Iterable[SeekRange]) -> Generator[SeekRange, None, None]:
        for seek_range in seek_ranges:
            print(seek_range)
            yield SeekRange(self.search_frame_before(seek_range.ss), self.search_frame_after(seek_range.to))

    def search_frame_before(self, time: str) -> str:
        threshold = float(time)
        for index, frame in enumerate(self.list_frame):
            if float(frame) >= threshold:
                return self.list_frame[index - 1]
        return self.list_frame[-1]

    def search_frame_after(self, time: str) -> str:
        threshold = float(time)
        for index, frame in enumerate(reversed(self.list_frame)):
            if float(frame) <= threshold:
                return self.list_frame[min(-(index + 1) + self.INDEX_GAP_BETWEEN_FFPROBE_AND_FFMPEG, -1)]
        return self.list_frame[0]


if __name__ == "__main__":
    basicConfig(level=INFO)
    file_input = Path(sys.argv[1])
    file_make_zero = make_zero(file_input, SeekRange(None, None))
    frames = Frames(file_make_zero)
    list_index = sorted([int(file.stem) for file in Path("./output").glob("*.jpg")])
    print(list_index)
    print(len(list_index))
    file_times = Path("output/times.json")
    list_time = json.loads(file_times.read_text(encoding="utf-8"))
    for index, time in enumerate(list_time):
        print(index, time)
    list_consecutive_period = create_list_consecutive_period(list_index)
    list_period = create_list_period(list_consecutive_period, list_time)
    seek_ranges = frames.search_outside_neighbor_frame(list_period)
    print(seek_ranges)
    for index, seek_range in enumerate(seek_ranges):
        print(seek_range)
        file_output = Path(f"{file_input.stem}-{index + 1}{file_input.suffix}")
        cut(file_input, seek_range, file_output)
        ffprobe.is_cut_by_key_frame_at_start(file_output)
        ffprobe.is_cut_by_key_frame_at_end(file_output)
        ffprobe.is_preserving_metadata(file_input, file_output)
