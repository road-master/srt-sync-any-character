from datetime import datetime, timedelta
from typing import Optional

__all__ = ["SeekRange"]

DATE_FORMAT = "%H:%M:%S.%f"


class SeekRange:
    def __init__(
        self,
        delta_offset: timedelta,
        *,
        string_from: Optional[str] = None,
        string_to: Optional[str] = None,
    ) -> None:
        self.datetime_zero = datetime.strptime("00:00:00.000", DATE_FORMAT)
        self.delta_offset = delta_offset
        self.ss = self.string_to_timedelta(string_from)
        self.to = self.string_to_timedelta(string_to)

    def string_to_timedelta(self, time_string: Optional[str]) -> Optional[timedelta]:
        if time_string is None:
            return None
        time_datetime = datetime.strptime(time_string, DATE_FORMAT)
        return (time_datetime - self.datetime_zero) + self.delta_offset
