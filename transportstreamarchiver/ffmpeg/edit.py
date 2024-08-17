from logging import getLogger
from pathlib import Path

from transportstreamarchiver.ffmpeg.execution import execute_ffmpeg
from transportstreamarchiver.ffmpeg.seek_range import SeekRange

__all__ = ["cut", "compress", "export_subtitle", "import_subtitle"]

logger = getLogger(__name__)


def cut(file_input: Path, ffmpeg_seek_range: SeekRange, file_output: Path) -> None:
    if not file_input.exists():
        msg = f"{file_input} does not exist"
        raise FileNotFoundError(msg)
    parameters = []
    if ffmpeg_seek_range.ss is not None:
        parameters.extend(["-ss", f"{ffmpeg_seek_range.ss}"])
    if ffmpeg_seek_range.to is not None:
        parameters.extend(["-to", f"{ffmpeg_seek_range.to}"])
    parameters.extend(
        [
            # To prevent following error:
            # [mpegts @ 000001f37d4fecc0] sample rate not set
            # [out#0/mpegts @ 000001f37afaa840] Could not write header (incorrect codec parameters ?): Invalid argument
            # Conversion failed!
            #
            # The broadcasted stream tends to be poor samples to analyze.
            # - Answer: ffmpeg not copying audio from concatenated VOB files. Says sample rate not set - Super User
            #   https://superuser.com/a/1609481
            # - ffmpegのオプション -analyzeduration と -probesize - 脳内メモ++
            #   http://fftest33.blog.fc2.com/blog-entry-109.html
            "-analyzeduration",
            "100000G",
            "-probesize",
            "100000G",
            "-i",
            str(file_input),
            # In default, only one stream is selected for each type and the rest of the streams are removed.
            "-map",
            "0",
            # In case when recorded video around the time when switch audio track
            # from single audio track to the one with sub audio,
            # the audio track may be handled as invalid track.
            # To remove useless track, set the following option:
            # "-map",
            # "-0:a:1",  # noqa: ERA001
            "-c",
            "copy",
            # To fix gap between video and audio track if they are not synchronized.
            "-async",
            "1",
            # (Just in case) To prepare in case when need to use experimental features
            "-strict",
            "experimental",
            # To fix timestamp in case when the video starts from negative timestamp.
            "-avoid_negative_ts",
            "make_non_negative",
            "-y",
            "-loglevel",
            "verbose",
            str(file_output),
            # The option `-copyts` is not used intentionally since `-copyts` has side effect
            # to
            # - ffmpeg Documentation
            #   https://www.ffmpeg.org/ffmpeg-all.html
            # > -dts_delta_threshold threshold
            # > The timestamp discontinuity correction ... is automatically disabled
            # > when employing the -copyts option (unless wrapping is detected).
            # > If a timestamp discontinuity is detected whose absolute value is greater than threshold,
            # > ffmpeg will remove the discontinuity by decreasing/increasing the current DTS and PTS
            # > by the corresponding delta value.
        ],
    )
    execute_ffmpeg(parameters, "Failed to cut", file_output)


def compress(file_input: Path, ffmpeg_seek_range: SeekRange, file_output: Path) -> None:
    # `-fix_sub_duration` requires to set before `-i` to load ARIB caption from input file.
    parameters = ["-fix_sub_duration", "-i", str(file_input)]
    # Requires to set after `-i`
    # otherwise `to` is added `ss` as offset,
    # therefore unnecessary segment will remain in output file.
    if ffmpeg_seek_range.ss is not None:
        parameters.extend(["-ss", f"{ffmpeg_seek_range.ss}"])
    # Requires to set after `-i`
    # otherwise empty frames are inserted
    # from the time: `to` to the end time of input file.
    if ffmpeg_seek_range.to is not None:
        parameters.extend(["-to", f"{ffmpeg_seek_range.to}"])
    parameters.extend(
        [
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
        ],
    )
    execute_ffmpeg(parameters, "Failed to cut", file_output)


def export_subtitle(file_input: Path, file_output: Path) -> None:
    parameters = [
        "-fix_sub_duration",
        "-i",
        str(file_input),
        "-c:s",
        "text",
        "-y",
        str(file_output),
    ]
    execute_ffmpeg(parameters, "Failed to export subtitle", file_output)


def import_subtitle(ts: Path, subtitle: Path, output: Path) -> None:
    parameters = [
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
    execute_ffmpeg(parameters, "Failed to import subtitle", output)
