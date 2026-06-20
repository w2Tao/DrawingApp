import tkinter as tk
from abc import ABC, abstractmethod

class DrawingElement(ABC):
    """
    绘图元素抽象基类，定义所有图形实体的通用接口，支持原型克隆。
    """
    def __init__(self, x, y, width, height, fill_color="#ffffff", stroke_color="#000000", stroke_width=2):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill_color = fill_color  # 如果为空字符串 ""，则代表透明填充
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.is_selected = False

    @abstractmethod
    def draw(self, canvas: tk.Canvas):
        """将当前图形渲染到 Canvas 上"""
        pass

    @abstractmethod
    def is_point_inside(self, px, py) -> bool:
        """用于鼠标点击选中检测"""
        pass

    @abstractmethod
    def clone(self) -> 'DrawingElement':
        """原型模式的核心：克隆自身"""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """状态序列化"""
        pass

    def move(self, dx, dy):
        """平面移动"""
        self.x += dx
        self.y += dy

    def resize(self, dw, dh):
        """调整大小"""
        self.width = max(10, self.width + dw)
        self.height = max(10, self.height + dh)