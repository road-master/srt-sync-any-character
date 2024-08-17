from logging import basicConfig, INFO
from pathlib import Path
import sys

from transportstreamarchiver import ffprobe

if __name__ == "__main__":
    basicConfig(level=INFO)
    file = Path(sys.argv[1])
    ffprobe.is_cut_by_key_frame_at_start(file)
    ffprobe.is_cut_by_key_frame_at_end(file)
