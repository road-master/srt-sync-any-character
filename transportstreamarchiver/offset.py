from datetime import timedelta
from logging import getLogger
from pathlib import Path

from transportstreamarchiver.ffmpeg.make_zero import make_zero
from transportstreamarchiver.ffmpeg.seek_range import SeekRange
from transportstreamarchiver.ffprobe.key_frame import inspect_frame


class OffsetChecker:
    def __init__(self, file: Path) -> None:
        self.logger = getLogger(__name__)
        self.file = file
        self._offset = None

    @property
    def offset(self) -> timedelta:
        return self._offset if self._offset else self.get_offset()

    def get_offset(self) -> timedelta:
        if not self.file.exists():
            msg = f"{self.file} does not exist"
            raise FileNotFoundError(msg)
        self.copy_only_beginning_with_making_zero()
        file_make_zero = self.file.parent / Path(f"{self.file.stem}_make_zero.ts")
        list_frame = inspect_frame(file_make_zero)
        file_make_zero.unlink()
        return list_frame[0].time

    def copy_only_beginning_with_making_zero(self) -> None:
        ffmpeg_seek_range = SeekRange(
            delta_offset=timedelta(days=0, seconds=0, microseconds=0),
            string_to="00:00:01.000",
        )
        make_zero(self.file, ffmpeg_seek_range)
