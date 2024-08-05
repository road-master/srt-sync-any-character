"""This module implements exceptions for this package."""

__all__ = ["FFprobeProcessError"]


class Error(Exception):
    """Base class for exceptions in this module.

    @see https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions
    """


class FFprobeProcessError(Error):
    """FFprobe process failed."""
