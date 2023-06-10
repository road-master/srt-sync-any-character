from datetime import datetime, timedelta
from typing import Union


__all__ = ["SeekRange"]


DATE_FORMAT = "%H:%M:%S.%f"


class SeekRange:
    def __init__(self, offset: Union[timedelta, str], string_from: str, string_to: str) -> None:
        self.datetime_zero = datetime.strptime("00:00:00.000", DATE_FORMAT)
        delta_offset = self.get_delta_offset(offset)
        datetime_from = datetime.strptime(string_from, DATE_FORMAT)
        datetime_to = datetime.strptime(string_to, DATE_FORMAT)
        self.ss = (datetime_from - self.datetime_zero) + delta_offset
        self.to = (datetime_to - self.datetime_zero) + delta_offset

    def get_delta_offset(self, offset: Union[timedelta, str]) -> timedelta:
        if isinstance(offset, timedelta):
            return offset
        datetime_offset = datetime.strptime(offset, DATE_FORMAT)
        return datetime_offset - self.datetime_zero
