from abc import ABC, abstractmethod

class Command(ABC):
    """
    命令抽象基类 (命令模式)
    """
    @abstractmethod
    def execute(self): 
        pass
        
    @abstractmethod
    def undo(self): 
        pass