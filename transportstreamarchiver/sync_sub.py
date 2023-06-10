from pathlib import Path

from srt_sync import SrtSyncWrapper
from transportstreamarchiver import ffmpeg


def sync_sub(ts_original: Path, remove_list: Path, ts_cut: Path, ts_synced: Path) -> None:
    sub_original = Path("sub.srt")
    sub_cut = Path(f"{sub_original.stem}_cut.srt")
    ffmpeg.export_subtitle(ts_original, sub_original)
    SrtSyncWrapper.process(sub_original, remove_list)
    ffmpeg.import_subtitle(ts_cut, sub_cut, ts_synced)
