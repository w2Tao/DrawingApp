import tkinter as tk
from .base import DrawingElement

class TextElement(DrawingElement):
    """独立的文本框元素"""
    def __init__(self, x, y, width, height, text="", fill_color="", stroke_color="#000000", font_size=12, stroke_width=1):
        super().__init__(x, y, width, height, fill_color, stroke_color, stroke_width)
        self.text = text
        self.font_size = font_size

    def draw(self, canvas: tk.Canvas):
        # 若设置了填充色，则绘制背景板
        if self.fill_color:
            canvas.create_rectangle(
                self.x, self.y, self.x + self.width, self.y + self.height,
                fill=self.fill_color, outline=""
            )
        canvas.create_text(
            self.x + self.width / 2, self.y + self.height / 2,
            text=self.text, fill=self.stroke_color,
            font=("Arial", int(self.font_size)),
            width=max(10, self.width - 6)
        )

    def is_point_inside(self, px, py) -> bool:
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height

    def clone(self) -> 'TextElement':
        cloned = TextElement(self.x, self.y, self.width, self.height, self.text, self.fill_color, self.stroke_color, self.font_size, self.stroke_width)
        cloned.is_selected = self.is_selected
        return cloned

    def to_dict(self) -> dict:
        return {
            "type": "Text", "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "text": self.text, "fill_color": self.fill_color, "stroke_color": self.stroke_color,
            "font_size": self.font_size, "stroke_width": self.stroke_width
        }