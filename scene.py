import json
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING

import ffmpeg

if TYPE_CHECKING:
    from ffmpeg.nodes import FilterableStream, OutputStream


def extract_scene(file_input: Path) -> str:
    stream_input: FilterableStream = ffmpeg.input(file_input)
    stream_filter_1: FilterableStream = ffmpeg.filter(stream_input, "select", "gt(scene,0.1)")
    stream_filter_2: FilterableStream = ffmpeg.filter(stream_filter_1, "scale", width=640, height=360)
    # To output the frame number and timestamp
    stream_filter_3: FilterableStream = ffmpeg.filter(stream_filter_2, "showinfo")
    # vsync="vfr": To prevent duplicate frames in same timestamp
    stream_output: OutputStream = ffmpeg.output(stream_filter_3, "output/%06d.jpg", vsync="vfr", hide_banner=None)
    bytes_stdout, bytes_stderr = ffmpeg.run(stream_output, capture_stdout=True, capture_stderr=True)
    print(bytes_stdout.decode("utf-8", errors="ignore"))
    return bytes_stderr.decode("utf-8", errors="ignore")


def getEndTime(stderr: str) -> str:
    date_pattern = re.compile(r"Duration\:\s(\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?)")
    timestamp: str = re.findall(date_pattern, stderr)[0]
    splits = timestamp.split(".")
    digits = splits[0].split(":")
    seconds = int(digits[0]) * 3600 + int(digits[1]) * 60 + int(digits[2])
    return f"{seconds}.{splits[1]}"


def getTimes(stderr: str) -> list[str]:
    pattern = r"pts_time:(\d+\.\d+)"  # pts_timeの数値を抽出する
    return re.findall(pattern, stderr)


if __name__ == "__main__":
    stderr = extract_scene(Path(sys.argv[1]))
    Path("output/std_err.txt").write_text(stderr, encoding="utf-8")
    print(stderr)
    list_time = ["0"]
    list_time.extend(getTimes(stderr))
    list_time.append(getEndTime(stderr))
    print(list_time)
    file_times = Path("output/times.json")
    file_times.write_text(json.dumps(list_time), encoding="utf-8")
    json.loads(file_times.read_text(encoding="utf-8"))
