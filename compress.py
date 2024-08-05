from pathlib import Path
import sys

from transportstreamarchiver.compress import compress

SYS_ARGV_LENGTH_TO_STRING_FROM = 3
SYS_ARGV_LENGTH_TO_STRING_TO = 4

if __name__ == "__main__":
    string_from = sys.argv[3] if len(sys.argv) > SYS_ARGV_LENGTH_TO_STRING_FROM else None
    string_to = sys.argv[4] if len(sys.argv) > SYS_ARGV_LENGTH_TO_STRING_TO else None
    compress(Path(sys.argv[1]), Path(sys.argv[2]), string_from=string_from, string_to=string_to)
