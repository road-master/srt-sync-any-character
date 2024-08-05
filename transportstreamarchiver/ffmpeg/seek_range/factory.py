from datetime import timedelta
from pathlib import Path
from typing import Optional

from transportstreamarchiver.ffmpeg.seek_range import SeekRange
from transportstreamarchiver.offset import OffsetChecker


class SeekRangeFactory:

    @classmethod
    def create(cls, file: Path, *, string_from: Optional[str] = None, string_to: Optional[str] = None) -> SeekRange:
        return SeekRange(cls.get_delta_offset(file), string_from=string_from, string_to=string_to)

    @staticmethod
    def get_delta_offset(file_input: Path) -> timedelta:
        if not file_input.exists():
            raise FileNotFoundError(f"{file_input} does not exist")
        return OffsetChecker(file_input).offset
