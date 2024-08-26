from pathlib import Path
import sys

from transportstreamarchiver.ffprobe.metadata import get_dict_stream

if __name__ == "__main__":
    get_dict_stream(Path(sys.argv[1]))
