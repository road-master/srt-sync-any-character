from datetime import timedelta
import logging
from logging import getLogger
from pathlib import Path

from mpv import backend, MPV

logging.basicConfig(level=logging.DEBUG)


class OffsetChecker:
    def __init__(self, file: Path) -> None:
        self.logger = getLogger(__name__)
        self.logger.debug("Backend: %s", backend)
        self.mpv = MPV(log_handler=print, pause=True, window_minimized=True)
        self.mpv.play(str(file))
        self.mpv.wait_for_event("file-loaded")
        while not self.mpv.time_pos:
            self.logger.debug("time_pos: %s", self.mpv.time_pos)

    @property
    def offset(self) -> timedelta:
        return timedelta(seconds=self.mpv.time_pos)
