"""
安装器基类
"""

from abc import ABC, abstractmethod
from typing import Tuple


class BaseInstaller(ABC):
    """安装器基类"""
    
    @abstractmethod
    def install(self) -> Tuple[bool, str]:
        """
        执行安装
        
        Returns:
            (成功标志, 详细信息)
        """
        pass
    
    @abstractmethod
    def check_status(self) -> bool:
        """
        检查安装状态
        
        Returns:
            是否已安装
        """
        pass
