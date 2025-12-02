"""
日誌工具模組

提供統一的日誌設定和取得 logger 的方法
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """
    設定全域日誌格式
    
    Args:
        level: 日誌等級 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 設定格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # 設定 root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 移除既有的 handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    root_logger.addHandler(console_handler)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    取得指定名稱的 logger
    
    Args:
        name: Logger 名稱，通常使用 __name__
        level: 可選的日誌等級覆蓋
        
    Returns:
        設定好的 Logger 實例
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("This is an info message")
    """
    logger = logging.getLogger(name)
    
    if level:
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(log_level)
    
    return logger


class LoggerMixin:
    """
    Logger Mixin 類別
    
    讓類別可以方便地使用 logger
    
    Example:
        >>> class MyService(LoggerMixin):
        ...     def do_something(self):
        ...         self.logger.info("Doing something")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """取得以類別名稱命名的 logger"""
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
