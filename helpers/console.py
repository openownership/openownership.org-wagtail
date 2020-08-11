# -*- coding: utf-8 -*-

"""
    utils.console
    ~~~~~~~~~~~~~~~
    Console level logging that doesn't barf on unicode.
"""

from __future__ import absolute_import, unicode_literals

import os
import sys
import math
import inspect
from typing import Optional, Any

import arrow
from django.conf import settings
from loguru import logger as guru

from .colours import blue, cyan, green, magenta, orange, red, bg_blue  # NOQA


LOG_LEVELS = {
    'INFO': 1,
    'SUCCESS': 2,
    'TEMPLATE': 3,
    'WARN': 4,
    'ERROR': 5
}

CLEAR = '\033[K'
HIDE_CURSOR = '\033[?25l'
SHOW_CURSOR = '\033[?25h'


class Logger(object):

    def __init__(self):
        self.terminal = sys.stdout
        self.writing_progress = False
        self.spindex = 0

    def _check_log_level(self, called_level: str) -> bool:
        """Check whether we want to actually output this message.

        Args:
            called_level (str): The level of the calling function - INFO, SUCCESS, WARN or ERROR

        Returns:
            bool: Whether we should output the message
        """
        try:
            level_str = settings.CONSOLE_LOG_LEVEL
        except Exception:
            level_str = 'WARN'
        level = LOG_LEVELS[level_str]
        called = LOG_LEVELS[called_level]
        if called >= level:
            return True
        else:
            return False

    def _get_code_position(self, curframe):
        frame = inspect.getouterframes(curframe, 0)
        base = os.getcwd()
        try:
            pos = '{}:{}'.format(frame[1].filename.replace(base, ''), frame[1].lineno)
        except IndexError:  # We couldn't get the stack info for some reason
            return '¯\\_(ツ)_/¯'
        else:
            return pos

    def _output(self, prefix: str, msg: str, extra: Any) -> None:
        print('{}\n> {} {}'.format(prefix, decode(msg), extra if extra else ''))

    def _ts(self) -> str:
        return magenta(str(arrow.now().format('H:mm:ss')))

    def info(self, msg: str, extra=None) -> bool:
        """Output a message in the INFO style

        Args:
            msg (str): The message you want to output
            extra (None, optional): Anything else you want added to the message
        """
        if not self._check_log_level('INFO'):
            return False
        curframe = inspect.currentframe()
        pos = self._get_code_position(curframe)
        prefix = '{} - {} - {}'.format(self._ts(), blue('INFO'), pos)
        if settings.DEBUG:
            self._output(prefix, msg, extra)
        else:
            guru.info(f'{prefix} - {msg} - {extra}')
        return True

    def warn(self, msg: str, extra=None) -> bool:
        """Output a message in the WARN style

        Args:
            msg (str): The message you want to output
            extra (None, optional): Anything else you want added to the message
        """
        if not self._check_log_level('WARN'):
            return False
        curframe = inspect.currentframe()
        pos = self._get_code_position(curframe)
        prefix = '{} - {} - {}'.format(self._ts(), orange('WARN'), pos)
        self._output(prefix, msg, extra)
        if settings.DEBUG:
            self._output(prefix, msg, extra)
        else:
            guru.warning(f'{prefix} - {msg} - {extra}')
        return True

    def error(self, msg: str, extra=None) -> bool:
        """Output a message in the ERROR style

        Args:
            msg (str): The message you want to output
            extra (None, optional): Anything else you want added to the message
        """
        if not self._check_log_level('ERROR'):
            return False
        curframe = inspect.currentframe()
        pos = self._get_code_position(curframe)
        prefix = '{} - {} - {}'.format(self._ts(), red('ERROR'), pos)
        if settings.DEBUG:
            self._output(prefix, msg, extra)
        else:
            guru.error(f'{prefix} - {msg} - {extra}')
        return True

    def success(self, msg: str, extra=None) -> bool:
        """Output a message in the SUCCESS style

        Args:
            msg (str): The message you want to output
            extra (None, optional): Anything else you want added to the message
        """
        if not self._check_log_level('SUCCESS'):
            return False
        curframe = inspect.currentframe()
        pos = self._get_code_position(curframe)
        prefix = '{} - {} - {}'.format(self._ts(), green('SUCCESS'), pos)
        if settings.DEBUG:
            self._output(prefix, msg, extra)
        else:
            guru.success(f'{prefix} - {msg} - {extra}')
        return True

    def template(self, msg: str, extra=None) -> bool:
        """Output a message in the TEMPLATE style

        Args:
            msg (str): The message you want to output
            extra (None, optional): Anything else you want added to the message
        """
        if not self._check_log_level('TEMPLATE'):
            return False
        curframe = inspect.currentframe()
        pos = self._get_code_position(curframe)
        prefix = '{} - {} - {}'.format(self._ts(), magenta('TEMPLATE'), pos)
        if settings.DEBUG:
            self._output(prefix, msg, extra)
        else:
            guru.success(f'{prefix} - {msg} - {extra}')
        return True

    def progress(self, msg: str = '', perc=0):
        spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        if self.spindex == len(spinner_frames) - 1:
            self.spindex = 0
        else:
            self.spindex += 1
        message = blue(self._parse(msg))
        self.terminal.write('\r{}'.format(CLEAR))
        self.terminal.flush()
        blocks = math.floor(perc / 5)
        spaces = math.ceil((100 - perc) / 5)
        human = f'{perc:.4f}'
        self.terminal.write(
            ' [{}{}] {} {}% {}\r'.format(
                bg_blue(' ') * blocks,
                ' ' * spaces, magenta(spinner_frames[self.spindex]), human, message
            )
        )
        self.terminal.flush()
        self.writing_progress = True

    def _parse(self, msg):
        if isinstance(msg, str):
            return msg
        else:
            try:
                return str(msg)
            except Exception:
                raise


logger = Logger()  # NOQA
console = logger


def decode(val):
    """Try to decode a string, and don't stop code execution if it fails.

    Args:
        val (str): Should be a string.

    Returns:
        str: Should also be a string.
    """
    if val is None or str(val) == str(''):
        return None

    if str(str(val).strip()) == str('NULL'):
        return None

    try:
        return val.decode('utf-8')
    except Exception:
        try:
            return val.decode('latin-1')
        except Exception:
            try:
                return val.decode('ascii')
            except Exception as e:
                pass

    return val
