"""
裝飾器模組

提供專案中常用的裝飾器
"""

import asyncio
import functools
import time
from typing import Callable, Optional, Type, Union

from lib.logger import get_logger


def log_execution(func: Callable) -> Callable:
    """
    記錄函數執行的裝飾器
    
    自動記錄函數的開始、結束和執行時間
    
    Example:
        >>> @log_execution
        ... async def my_function():
        ...     pass
    """
    logger = get_logger(func.__module__)
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Failed {func.__name__} after {elapsed:.3f}s: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Failed {func.__name__} after {elapsed:.3f}s: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    重試裝飾器
    
    在函數失敗時自動重試
    
    Args:
        max_attempts: 最大嘗試次數
        delay: 初始延遲秒數
        backoff: 延遲倍數 (每次重試延遲乘以此值)
        exceptions: 要捕捉的例外類型
        
    Example:
        >>> @retry(max_attempts=3, delay=1.0)
        ... async def unstable_function():
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        logger = get_logger(func.__module__)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
            
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
            
            raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def deprecated(message: Optional[str] = None) -> Callable:
    """
    標記函數為已棄用的裝飾器
    
    Args:
        message: 棄用訊息
        
    Example:
        >>> @deprecated("Use new_function instead")
        ... def old_function():
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        logger = get_logger(func.__module__)
        warn_msg = message or f"{func.__name__} is deprecated"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.warning(f"DEPRECATED: {warn_msg}")
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
