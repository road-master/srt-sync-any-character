from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
import difflib
import json
from pathlib import Path
import subprocess
from textwrap import dedent
from typing import Any

from deepdiff import DeepDiff

from transportstreamarchiver.ffprobe.exceptions import FFprobeProcessError

__all__ = ["is_preserving_metadata"]


def get_metadata(file: Path) -> Any:
    # video - ffmpeg Cut a media preserving all streams but also all metadata, timecodes and everything else - Video Production Stack Exchange
    # https://video.stackexchange.com/a/34334
    args = [
        "-show_entries",
        "program:stream:program_tags:stream_tags:format_tags",
        "-output_format",
        "json",
        "-loglevel",
        "repeat+fatal",
    ]
    command = ["ffprobe", *args, str(file)]
    # Reason: Confirmed that command isn't so risky.
    completed_process = subprocess.run(command, text=True, capture_output=True)  # noqa: S603
    return json.loads(completed_process.stdout)


RED: Callable[[str], str] = lambda text: f"\u001b[31m{text}\033\u001b[0m"
GREEN: Callable[[str], str] = lambda text: f"\u001b[32m{text}\033\u001b[0m"


def get_edits_string(old: str, new: str) -> str:
    """Get human readable diff string.

    - Answer: python - How to make DeepDiff output human readable? - Stack Overflow
      https://stackoverflow.com/a/74336612/12721873
    """
    result = ""

    lines = difflib.ndiff(old.splitlines(keepends=True), new.splitlines(keepends=True))

    for line in lines:
        striped_line = line.rstrip()
        if striped_line.startswith("+"):
            result += GREEN(striped_line) + "\n"
        elif striped_line.startswith("-"):
            result += RED(striped_line) + "\n"
        elif striped_line.startswith("?"):
            continue
        else:
            result += striped_line + "\n"

    return result


def is_preserving_metadata(file_input: Path, file_output: Path) -> None:
    metadata_input = get_metadata(file_input)
    metadata_output = get_metadata(file_output)
    # Since FFmpeg doesn't preserve the order of streams even if we specify stream order by `-map` option.
    # The option `-program` might block to preserve the order of streams.
    last_stream = metadata_output["streams"].pop(-1)
    metadata_output["streams"].insert(0, last_stream)
    index_program_empty = "1"
    exclude_regex_paths = [
        # The metadata that is changed by cut by FFmpeg.
        r"root\['programs'\]\[\d+\]\['pcr_pid'\]",
        r"root\['programs'\]\[\d+\]\['streams'\]\[\d+\]\['index'\]",
        r"root\['programs'\]\[\d+\]\['streams'\]\[\d+\]\['ts_id'\]",
        r"root\['programs'\]\[\d+\]\['streams'\]\[\d+\]\['id'\]",
        r"root\['programs'\]\[\d+\]\['streams'\]\[\d+\]\['start_pts'\]",
        r"root\['programs'\]\[\d+\]\['streams'\]\[\d+\]\['start_time'\]",
        r"root\['programs'\]\[\d+\]\['streams'\]\[\d+\]\['duration_ts'\]",
        r"root\['programs'\]\[\d+\]\['streams'\]\[\d+\]\['duration'\]",
        r"root\['programs'\]\[\d+\]\['streams'\]\[\d+\]\['bit_rate'\]",
        r"root\['streams'\]\[\d+\]\['index'\]",
        r"root\['streams'\]\[\d+\]\['ts_id'\]",
        r"root\['streams'\]\[\d+\]\['id'\]",
        r"root\['streams'\]\[\d+\]\['r_frame_rate'\]",
        r"root\['streams'\]\[\d+\]\['avg_frame_rate'\]",
        r"root\['streams'\]\[\d+\]\['start_pts'\]",
        r"root\['streams'\]\[\d+\]\['start_time'\]",
        r"root\['streams'\]\[\d+\]\['duration_ts'\]",
        r"root\['streams'\]\[\d+\]\['duration'\]",
        r"root\['streams'\]\[\d+\]\['bit_rate'\]",
        # Since FFmpeg can't create empty program.
        rf"root\['programs'\]\[{index_program_empty}\]",
        # Since FFmpeg can't copy unrecognized codec.
        r"root\['streams'\]\[0\]\['codec_name'\]",
        r"root\['streams'\]\[0\]\['codec_long_name'\]",
        r"root\['streams'\]\[0\]\['codec_type'\]",
        # Since service_provider was empty.
        r"root\['programs'\]\[0\]\['tags'\]\['service_provider'\]",
    ]
    deep_diff = DeepDiff(metadata_input, metadata_output, exclude_regex_paths=exclude_regex_paths)
    if not deep_diff:
        return
    metadata_input_string = json.dumps(metadata_input, indent=2, sort_keys=True)
    metadata_output_string = json.dumps(metadata_output, indent=2, sort_keys=True)
    human_readable_diff = get_edits_string(metadata_input_string, metadata_output_string)
    msg = dedent(
        f"""
            Metadata is not preserved.
            {human_readable_diff}
            {json.dumps(json.loads(deep_diff.to_json()), indent=2)}
        """,
    )
    raise FFprobeProcessError(msg)


@dataclass
class Program:
    id: int
    stream_indices: list[int]
    tags: dict[str, str] | None


@dataclass
class Entries:
    programs: list[Program]
    orphaned_streams: list[dict[str, str]]


@dataclass
class Stream:
    index: int
    tags: dict[str, str] | None
    program: Program | None


def create_program(program: dict[str, Any]) -> Program:
    program_id = program["program_id"]
    stream_indices = [stream["index"] for stream in program["streams"]]
    tags = program.get("tags")
    return Program(program_id, stream_indices, tags)


def get_dict_stream(file: Path) -> dict[int, Stream]:
    metadata = get_metadata(file)
    print(json.dumps(metadata, indent=2))
    programs = {stream["index"]: create_program(prog) for prog in metadata["programs"] for stream in prog["streams"]}
    streams = {
        stream["index"]: Stream(stream["index"], stream.get("tags"), programs.get(stream["index"]))
        for stream in metadata["streams"]
    }
    return dict(sorted(streams.items()))
