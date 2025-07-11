import logging
import inspect
from rich.console import Console
from rich.traceback import Traceback


class Logger:
    _logger = logging.getLogger("uvicorn")
    _console = Console()

    @classmethod
    def _log(cls, level: str, message: str, **kwargs):
        frame = inspect.stack()[2]
        filename = frame.filename.split("\\")[-1]
        function = frame.function
        log_msg = f"{filename} : {function} :\n\t  {message}"
        getattr(cls._logger, level)(log_msg, **kwargs)

    @classmethod
    def info(cls, message: str, **kwargs):
        cls._log("info", message, **kwargs)

    @classmethod
    def warning(cls, message: str, **kwargs):
        cls._log("warning", message, **kwargs)

    @classmethod
    def error(
        cls,
        message: str,
        exc: Exception = None,
        max_traceback_levels: int = 1,
        **kwargs,
    ):
        cls._log("error", message, **kwargs)
        if exc:
            cls._console.print(
                Traceback.from_exception(
                    type(exc),
                    exc,
                    exc.__traceback__,
                    show_locals=False,
                    max_frames=max_traceback_levels,
                )
            )
