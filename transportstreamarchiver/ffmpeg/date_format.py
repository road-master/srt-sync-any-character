from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from transportstreamarchiver.offset import OffsetChecker

__all__ = ["SeekRange"]

DATE_FORMAT = "%H:%M:%S.%f"


class SeekRange:
    def __init__(
        self,
        file_input: Path,
        *,
        string_from: Optional[str] = None,
        string_to: Optional[str] = None,
        delta_offset: Optional[timedelta] = None,
    ) -> None:
        self.datetime_zero = datetime.strptime("00:00:00.000", DATE_FORMAT)
        self.delta_offset = delta_offset if delta_offset else self.get_delta_offset(file_input)
        self.ss = self.string_to_timedelta(string_from)
        self.to = self.string_to_timedelta(string_to)

    def get_delta_offset(self, file_input: Path) -> timedelta:
        if not file_input.exists():
            raise FileNotFoundError(f"{file_input} does not exist")
        return OffsetChecker(file_input).offset

    def string_to_timedelta(self, time_string: Optional[str]) -> Optional[timedelta]:
        if time_string is None:
            return None
        time_datetime = datetime.strptime(time_string, DATE_FORMAT)
        return (time_datetime - self.datetime_zero) + self.delta_offset
