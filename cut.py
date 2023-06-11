from pathlib import Path
import sys
from transportstreamarchiver.cut import cut

if __name__ == "__main__":
    string_from = sys.argv[3] if 3 < len(sys.argv) else None
    string_to = sys.argv[4] if 4 < len(sys.argv) else None
    cut(Path(sys.argv[1]), Path(sys.argv[2]), string_from=string_from, string_to=string_to)
