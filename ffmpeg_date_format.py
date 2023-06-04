from datetime import datetime


DATE_FORMAT = "%H:%M:%S.%f"


class FFmpegSeekRange:
    def __init__(self, string_base: str, string_from: str, string_to) -> None:
        datetime_zero = datetime.strptime("00:00:00.000", DATE_FORMAT)
        datetime_base = datetime.strptime(string_base, DATE_FORMAT)
        datetime_from = datetime.strptime(string_from, DATE_FORMAT)
        datetime_to = datetime.strptime(string_to, DATE_FORMAT)
        delta_base = datetime_base - datetime_zero
        self.ss = (datetime_from - datetime_zero) + delta_base
        self.to = (datetime_to - datetime_zero) + delta_base
