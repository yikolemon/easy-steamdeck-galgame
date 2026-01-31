"""
Base installer class
"""

from abc import ABC, abstractmethod
from typing import Tuple


class BaseInstaller(ABC):
    """Base installer class"""
    
    @abstractmethod
    def install(self) -> Tuple[bool, str]:
        """
        Perform installation
        
        Returns:
            (success_flag, detailed_message)
        """
        pass
    
    @abstractmethod
    def check_status(self) -> bool:
        """
        Check installation status
        
        Returns:
            Whether installed
        """
        pass
