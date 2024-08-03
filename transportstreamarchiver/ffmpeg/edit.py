import subprocess
from pathlib import Path

from transportstreamarchiver.ffmpeg import SeekRange
from transportstreamarchiver.ffmpeg.exceptions import FFmpegProcessError

__all__ = ["cut", "compress", "export_subtitle", "import_subtitle"]


def cut(file_input: Path, ffmpeg_seek_range: SeekRange, file_output: Path) -> None:
    if not file_input.exists():
        raise FileNotFoundError(f"{file_input} does not exist")
    command = ["ffmpeg"]
    if ffmpeg_seek_range.ss is not None:
        command.extend(["-ss", f'{ffmpeg_seek_range.ss}'])
    if ffmpeg_seek_range.to is not None:
        command.extend(["-to", f'{ffmpeg_seek_range.to}'])
    command.extend([
        "-i",
        str(file_input),
        "-map",
        "0",
        "-c",
        "copy",
        "-async",
        "1",
        "-strict",
        "-2",
        "-avoid_negative_ts",
        "1",
        "-y",
        str(file_output),
    ])
    print(" ".join(command))
    return_code = subprocess.call(command)
    if return_code != 0 or not file_output.exists():
        raise FFmpegProcessError("Failed to cut")


def compress(
    file_input: Path,
    ffmpeg_seek_range: SeekRange,
    file_output: Path,
) -> None:
    # `-fix_sub_duration` requires to set before `-i` to load ARIB caption from input file.
    command = ["ffmpeg", "-fix_sub_duration", "-i", str(file_input)]
    # Requires to set after `-i`
    # otherwise `to` is added `ss` as offset,
    # therefore unnecessary segment will remain in output file.
    if ffmpeg_seek_range.ss is not None:
        command.extend(["-ss", f'{ffmpeg_seek_range.ss}'])
    # Requires to set after `-i`
    # otherwise empty frames are inserted
    # from the time: `to` to the end time of input file.
    if ffmpeg_seek_range.to is not None:
        command.extend(["-to", f'{ffmpeg_seek_range.to}'])
    command.extend([
        "-c:a",
        "copy",
        "-c:v",
        "libx265",
        "-crf",
        "22",
        "-tag:v",
        "hvc1",
        "-vf",
        "w3fdif",
        "-c:s",
        "mov_text",
        "-metadata:s:s:0",
        "language=jpn",
        "-y",
        str(file_output),
    ])
    return_code = subprocess.call(command)
    if return_code != 0 or not file_output.exists():
        raise FFmpegProcessError("Failed to cut")


def export_subtitle(file_input: Path, file_output: Path) -> None:
    return_code = subprocess.call(
        [
            "ffmpeg",
            "-fix_sub_duration",
            "-i",
            str(file_input),
            "-c:s",
            "text",
            "-y",
            str(file_output),
        ]
    )
    if return_code != 0 or not file_output.exists():
        raise FFmpegProcessError("Failed to export subtitle")


def import_subtitle(ts: Path, subtitle: Path, output: Path) -> None:
    return_code = subprocess.call(
        [
            "ffmpeg",
            "-i",
            str(ts),
            "-i",
            str(subtitle),
            "-c",
            "copy",
            "-c:s",
            "mov_text",
            "-metadata:s:s:0",
            "language=jpn",
            "-y",
            str(output),
        ]
    )
    if return_code != 0 or not output.exists():
        raise FFmpegProcessError("Failed to import subtitle")
