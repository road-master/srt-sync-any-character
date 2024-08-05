from pathlib import Path

import pytest

from transportstreamarchiver.offset import OffsetChecker
from transportstreamarchiver.mpv.offset import OffsetChecker as MpvOffsetChecker


@pytest.mark.skip(reason="Since it's difficult to prepare copyright free MPEG ts file.")
def test() -> None:
    file_input = Path("input.ts")
    assert OffsetChecker(file_input).offset == MpvOffsetChecker(file_input).offset
