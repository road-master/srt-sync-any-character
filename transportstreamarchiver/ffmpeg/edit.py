from logging import getLogger
from pathlib import Path

from transportstreamarchiver.ffmpeg.execution import execute_ffmpeg
from transportstreamarchiver.ffmpeg.seek_range import SeekRange
from transportstreamarchiver.ffprobe.metadata import get_dict_stream

__all__ = ["cut", "compress", "export_subtitle", "import_subtitle"]

logger = getLogger(__name__)


class ParameterBuilder:
    def __init__(self) -> None:
        self.parameters_map: list[str] = []
        self.parameters_create_stream: list[str] = []
        self.parameters_map_metadata: list[str] = []
        self.parameters_metadata: list[str] = []

    def build(self, file_input: Path) -> None:
        dict_stream = get_dict_stream(file_input)
        list_processed_program_id = []
        output_stream_index = 0
        for index, stream in dict_stream.items():
            if not stream.program:
                self.parameters_map.extend(["-map", f"0:{index}"])
                self.parameters_map_metadata.extend([f"-map_metadata:s:{output_stream_index}", f"0:s:{index}"])
                output_stream_index += 1
                continue
            program = stream.program
            if program.id in list_processed_program_id:
                continue
            list_processed_program_id.append(program.id)
            self.parameters_map.extend(["-map", f"p:{program.id}?"])
            list_argument_stream = []
            for stream_index in program.stream_indices:
                self.parameters_map_metadata.extend([f"-map_metadata:s:{output_stream_index}", f"0:s:{stream_index}"])
                output_stream_index += 1
                list_argument_stream.append(f"st={stream_index}")

            argument_stream = ":".join(f"st={stream_id}" for stream_id in program.stream_indices)
            self.parameters_create_stream.extend(["-program", f"program_num={program.id}:{argument_stream}"])
            if not program.tags:
                continue
            for key, value in program.tags.items():
                self.parameters_metadata.extend(["-metadata:p", f"{key}={value}"])
        print(f"""
map = {self.parameters_map}
create_stream = {self.parameters_create_stream}
metadata = {self.parameters_metadata}
""")


def cut(file_input: Path, ffmpeg_seek_range: SeekRange, file_output: Path) -> None:
    if not file_input.exists():
        msg = f"{file_input} does not exist"
        raise FileNotFoundError(msg)
    # To prevent to FFmpeg overwrite some metadata.
    parameter_builder = ParameterBuilder()
    parameter_builder.build(file_input)
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
            *parameter_builder.parameters_map,
            # In case when recorded video around the time when switch audio track
            # from single audio track to the one with sub audio,
            # the audio track may be handled as invalid track.
            # To remove useless track, set the following option:
            # "-map",
            # "-0:a:1",  # noqa: ERA001
            *parameter_builder.parameters_create_stream,
            "-c",
            "copy",
            # To copy data stream that FFmpeg doesn't recognize:
            # - Answer: ffmpeg: Extract unknown data stream from video container - Stack Overflow
            #   https://stackoverflow.com/a/63053691/12721873
            "-copy_unknown",
            # To fix gap between video and audio track if they are not synchronized.
            "-async",
            "1",
            # To copy also metadata (this is not reliable):
            # - Retrieving and Saving media metadata using FFmpeg - Stack Overflow
            #   https://stackoverflow.com/questions/9464617/retrieving-and-saving-media-metadata-using-ffmpeg
            *parameter_builder.parameters_map_metadata,
            "-movflags",
            "use_metadata_tags",
            *parameter_builder.parameters_metadata,
            # (Just in case) To prepare in case when need to use experimental features
            "-strict",
            "experimental",
            # To fix timestamp in case when the video starts from negative timestamp.
            "-avoid_negative_ts",
            "make_non_negative",
            "-y",
            "-loglevel",
            "verbose",
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
    parameters.append(str(file_output))
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
