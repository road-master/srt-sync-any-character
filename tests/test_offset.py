from pathlib import Path

import pytest

from transportstreamarchiver.mpv.offset import OffsetChecker as MpvOffsetChecker
from transportstreamarchiver.offset import OffsetChecker


@pytest.mark.skip(reason="Since it's difficult to prepare copyright free MPEG ts file.")
def test() -> None:
    file_input = Path("input.ts")
    assert OffsetChecker(file_input).offset == MpvOffsetChecker(file_input).offset
