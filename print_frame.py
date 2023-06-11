from pathlib import Path
import sys

from transportstreamarchiver.ffprobe.key_frame import print_frame


if __name__ == "__main__":
    file_make_zero = Path(sys.argv[1])
    print_frame(file_make_zero)
