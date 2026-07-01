# -*- coding: utf-8 -*-
"""
日志模块 - 输出到 log/ 目录，按日期分文件
"""
import os
import logging
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "log")
_enabled = False
_logger = None


def _ensure_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def _get_log_path():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{today}.log")


def init(enabled=False):
    global _enabled, _logger
    _enabled = enabled
    if not enabled:
        return
    _ensure_dir()
    _logger = logging.getLogger("cat_guide")
    _logger.setLevel(logging.DEBUG)
    _logger.handlers.clear()
    fh = logging.FileHandler(_get_log_path(), encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
    fh.setFormatter(fmt)
    _logger.addHandler(fh)


def set_enabled(enabled):
    global _enabled
    _enabled = enabled
    if enabled:
        _ensure_dir()
    if _logger:
        _logger.handlers.clear()
        if enabled:
            fh = logging.FileHandler(_get_log_path(), encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
            fh.setFormatter(fmt)
            _logger.addHandler(fh)


def is_enabled():
    return _enabled


def log(msg):
    if _enabled and _logger:
        _logger.info(msg)
