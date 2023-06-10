from pathlib import Path
import sys
from transportstreamarchiver.cut import cut

if __name__ == "__main__":
    cut(Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4]))
