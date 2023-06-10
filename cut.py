from pathlib import Path
import sys
from transportstreamarchiver.cut import cut

if __name__ == "__main__":
    cut(Path("original.ts"), sys.argv[1], sys.argv[2], Path(sys.argv[3]))
