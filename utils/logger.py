import logging
import sys

from .getters import get_preferences

SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)


logging.Logger.success = success

logging.basicConfig(
    format="Gscatter - %(filename)s:%(lineno)d - %(levelname)s: %(message)s",
    level=20,
)
logger: logging.Logger = logging.getLogger(__name__)


def update_log_level(level: int | str):
    """Callback to update log level."""
    logger.setLevel(level)
    logger.info(f"Log level updated to {level}")


def debug(*args, sep=" ", end="\n"):
    """
    Debug function that works like print() but uses logging.info.
    - *args: Values to print.
    - sep: Separator between arguments (default: space).
    - end: String appended after the last value (default: newline).
    """
    msg = sep.join(map(str, args)) + end.strip("\n")  # Mimics print behavior
    logger.info(msg, stacklevel=2)


def info(*args, sep=" ", end="\n"):
    msg = sep.join(map(str, args)) + end.strip("\n")  # Mimics print behavior
    logger.info(msg)


def warn(*args, sep=" ", end="\n"):
    msg = sep.join(map(str, args)) + end.strip("\n")  # Mimics print behavior
    logger.warning(msg)


def success(*args, sep=" ", end="\n"):
    msg = sep.join(map(str, args)) + end.strip("\n")  # Mimics print behavior
    logger.success(msg)


def error(*args, sep=" ", end="\n"):
    msg = sep.join(map(str, args)) + end.strip("\n")  # Mimics print behavior
    prefs = get_preferences()
    DEBUG_ENABLED = prefs.enable_developer_mode
    code = sys._getframe().f_back.f_code
    if (debug and DEBUG_ENABLED) or not debug:
        logger.error(
            f"\n{code.co_name} in {code.co_filename}:{code.co_firstlineno}>: {msg}",
            stacklevel=2,
        )


def try_catch(function):
    def protected(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logging.warning("FAILED TO RUN %s \n %s" % (str(function), str(e)))
            return None

    return protected


def annotate(f):
    name = str(f).split(" ")[1]

    def f2(*args, **kwargs):
        debug(f"{name}(...): ==>")
        ret = f(*args, **kwargs)
        debug(f"    {name} <== {ret}")
        return ret

    return f2
