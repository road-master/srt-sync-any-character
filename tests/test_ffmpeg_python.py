from dataclasses import dataclass
import re
from typing import Optional

import ffmpeg
from ffmpeg.nodes import FilterableStream, OutputStream
import pytest


@dataclass
class Option:
    option: str
    argument: Optional[str] = None


def parse_option(line: str) -> Option:
    match = re.match(r"^Reading option '(.+)' \.\.\. matched as (.+)\.$", line)
    if match is None:
        msg = f"Failed to parse line: {line}"
        raise ValueError(msg)
    groups = match.groups()
    option = groups[0]
    leftover = groups[1]
    match = re.search(r"with argument '(.+)'$", leftover)
    argument = match.groups()[0] if match is not None else None
    return Option(option, argument)


def mock_output(stream: OutputStream, expects: list[Option]) -> OutputStream:
    expects.extend(
        [
            Option("-f", "null"),
            Option("/dev/null", None),
            Option("-loglevel", "debug"),
        ],
    )
    return ffmpeg.output(stream.node.incoming_edge_map[0][0].stream(), "/dev/null", f="null", loglevel="debug")


def parse_options(standard_error: str) -> list[Option]:
    pattern = re.compile(r"^Reading option '.*$", re.MULTILINE)
    list_line_option = pattern.findall(standard_error)
    return [parse_option(line) for line in list_line_option]


def assert_option(stream: OutputStream, expects: list[Option]) -> None:
    stream = mock_output(stream, expects)
    results = stream.run(capture_stdout=True, capture_stderr=True)
    out: bytes = results[0]
    err: bytes = results[1]
    assert out.decode("utf-8") == ""
    standard_error = err.decode("utf-8", errors="ignore")
    options = parse_options(standard_error)
    assert len(options) == len(expects)
    for option in options:
        assert option in expects


@pytest.mark.skip(reason="Since it's difficult to prepare copyright free MPEG ts file.")
def test() -> None:
    stream: FilterableStream = ffmpeg.input("input.ts", ss="00:00:00.000", to="00:00:02.000")
    expects = [
        Option("-ss", "00:00:00.000"),
        Option("-to", "00:00:02.000"),
        Option("-i", "input.ts"),
    ]
    stream = ffmpeg.output(stream, "input-3.ts")
    assert_option(stream, expects)
