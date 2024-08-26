from pathlib import Path
import sys

from transportstreamarchiver.ffprobe.metadata import is_preserving_metadata

if __name__ == "__main__":
    is_preserving_metadata(Path(sys.argv[1]), Path(sys.argv[2]))
