from pathlib import Path
import sys

from transportstreamarchiver.sync_sub import sync_sub


if __name__ == "__main__":
    ts_original = Path(sys.argv[1])
    remove_list = Path(sys.argv[2])
    ts_cut = Path(sys.argv[3])
    ts_synced = Path(sys.argv[4])
    sync_sub(ts_original, remove_list, ts_cut, ts_synced)
