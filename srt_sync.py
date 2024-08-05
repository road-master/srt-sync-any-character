from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
import shutil

# Reason: Using subprocess is necessary to call SrtSync.exe.
import subprocess  # nosec: B404
import sys
import textwrap

logger = getLogger(__name__)


class Error(Exception):
    """Base class for exceptions in this module.

    @see https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions
    """


class SrtSyncError(Error):
    """SrtSync failed."""


@dataclass
class Sub:
    index: int
    time: str
    text: str


Subs = dict[int, Sub]


def clear_file(file: str) -> Path:
    path = Path(file)
    if path.exists():
        path.unlink()
    return path


def load(file_sub: Path) -> Subs:
    subs = {}
    with suppress(StopIteration), file_sub.open(encoding="utf-8") as file:
        while True:
            line = next(file).strip()
            if not line.isdigit():
                continue
            index = int(line)
            subs[index] = Sub(index, next(file), next(file))
    return subs


def save(file_path: Path, subs: Subs, what_write_to_text: Callable[[Sub], str]) -> None:
    with file_path.open("w", encoding="utf-8") as file:
        for sub in subs.values():
            file.write(str(sub.index) + "\n")
            file.write(sub.time)
            file.write(what_write_to_text(sub))
            file.write("\n")


class SrtSync:
    EXECUTABLE = "SrtSync"

    def __init__(self, file_input: Path) -> None:
        self.input = file_input
        self.output = clear_file(f"{self.input.stem}_new.srt")
        if not shutil.which(self.EXECUTABLE):
            msg = textwrap.dedent(
                """\
                SrtSync not found.
                Put SrtSync.exe into either of PATH in Windows (or same folder with this Python code).
                If you don't have SrtSync.exe, download it from:
                http://www2.wazoku.net/2sen/
            """,
            )
            raise SrtSyncError(msg)

    def cut(self, remove_list: Path) -> Path:
        # Reason: Confirmed that command isn't so risky.
        process = subprocess.Popen(  # noqa: S603  # nosec: B603
            [self.EXECUTABLE, "-aviutldl", remove_list, self.input],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        while process.poll() is None:
            # Reason: The condition `process.poll() is None` guarantees that `process.stdout` is not None.
            line: str = process.stdout.readline()  # type: ignore[union-attr]
            stripped_line = line.strip()
            logger.debug(stripped_line)
            if stripped_line.startswith("続行するには何かキーを押してください"):
                process.communicate("\r\n")
        if not self.output.exists():
            msg = "Failed to cut"
            raise SrtSyncError(msg)
        return self.output


class SrtSyncWrapper:
    @classmethod
    def process(cls, file_sub_original: Path, remove_list: Path) -> None:
        file_sub_temporary = cls.replace_text_with_index(file_sub_original)
        file_sub_cut = SrtSync(file_sub_temporary).cut(remove_list)
        cls.replace_index_with_text(file_sub_cut, file_sub_original)

    @staticmethod
    def replace_text_with_index(file_sub_original: Path) -> Path:
        subs_original = load(file_sub_original)
        file_sub_temporary = clear_file(f"{file_sub_original.stem}_replaced_by_index.srt")
        save(file_sub_temporary, subs_original, lambda sub: f"\\{sub.index}\\\n")
        return file_sub_temporary

    @staticmethod
    def replace_index_with_text(file_sub_cut: Path, file_sub_original: Path) -> None:
        file_sub_cut_fixed = clear_file(f"{file_sub_original.stem}_cut.srt")
        subs_cut = load(file_sub_cut)
        subs_original = load(file_sub_original)
        save(file_sub_cut_fixed, subs_cut, lambda sub: subs_original[int(sub.text.replace("\\", ""))].text)


if __name__ == "__main__":
    SrtSyncWrapper.process(Path(sys.argv[2]), Path(sys.argv[1]))
