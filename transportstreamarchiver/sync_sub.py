from pathlib import Path

from srt_sync import SrtSyncWrapper
from transportstreamarchiver import ffmpeg


def sync_sub(ts_original: Path, remove_list: Path, ts_cut: Path) -> None:
    sub_original = Path("sub.srt")
    sub_cut = Path(f"{sub_original.stem}_cut.srt")
    file_output = Path("subtitled.mp4")
    ffmpeg.export_subtitle(ts_original, sub_original)
    SrtSyncWrapper.process(sub_original, remove_list)
    ffmpeg.import_subtitle(ts_cut, sub_cut, file_output)
