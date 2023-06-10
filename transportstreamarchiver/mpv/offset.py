from datetime import timedelta
from logging import getLogger
import logging
from pathlib import Path
import sys
from mpv import MPV, backend


logging.basicConfig(level=logging.DEBUG)


class OffsetChecker:
    def __init__(self, file: Path) -> None:
        self.logger = getLogger(__name__)
        self.logger.debug("Backend: %s", backend)
        self.mpv = MPV(
            log_handler=print,
            pause=True,
            window_minimized=True,
            # loglevel='debug',
        )
        self.mpv.play(str(file))
        self.mpv.wait_for_event("file-loaded")
        while not self.mpv.time_pos:
            self.logger.debug("time_pos: %s", self.mpv.time_pos)

    @property
    def offset(self) -> timedelta:
        return timedelta(seconds=self.mpv.time_pos)


if __name__ == "__main__":
    offset = OffsetChecker(Path(sys.argv[1])).offset
    print(offset)
