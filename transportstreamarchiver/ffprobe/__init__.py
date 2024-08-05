from transportstreamarchiver.ffprobe import key_frame

# Reason: To import all names from a submodule
from transportstreamarchiver.ffprobe.key_frame import *  # noqa: F401, F403, RUF100

__all__: list[str] = []
__all__ += key_frame.__all__
