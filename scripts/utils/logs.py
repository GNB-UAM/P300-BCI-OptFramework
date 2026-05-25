import sys
import logging


def cfg_logger(logger: logging.Logger,
               journalctl: bool = True) -> logging.Logger:
    '''
    This method will return the project's logger
    to debug applications. Such log will store
    its traces within journalctl's logs or stdout.

    :param name: String with the logger's name.
    :param journalctl: Whether to log to journalctl
    or stdout.

    :returns: **logging.Logger** -- the built
    logger.
    '''
    # Logging to journalctl or stdout
    if journalctl:
        from systemd.journal import JournalHandler
        handler = JournalHandler(SYSLOG_IDENTIFIER=logger.name)
    else:
        handler = logging.StreamHandler(sys.stdout)

    handler.formatter = logging.Formatter(
        "%(name)s [%(process)d] - %(levelname)s: %(funcName)s : %(message)s")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
