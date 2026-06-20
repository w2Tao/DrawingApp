import math
import tkinter as tk
from .base import DrawingElement

class RectangleElement(DrawingElement):
    """矩形/方框元素"""
    def draw(self, canvas: tk.Canvas):
        canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=self.fill_color if self.fill_color else "", 
            outline=self.stroke_color, width=self.stroke_width
        )

    def is_point_inside(self, px, py) -> bool:
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height

    def clone(self) -> 'RectangleElement':
        cloned = RectangleElement(self.x, self.y, self.width, self.height, self.fill_color, self.stroke_color, self.stroke_width)
        cloned.is_selected = self.is_selected
        return cloned

    def to_dict(self) -> dict:
        return {
            "type": "Rectangle", "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "fill_color": self.fill_color, "stroke_color": self.stroke_color, "stroke_width": self.stroke_width
        }


class CircleElement(DrawingElement):
    """正圆形元素"""
    def draw(self, canvas: tk.Canvas):
        diameter = min(self.width, self.height)
        canvas.create_oval(
            self.x, self.y, self.x + diameter, self.y + diameter,
            fill=self.fill_color if self.fill_color else "", 
            outline=self.stroke_color, width=self.stroke_width
        )

    def is_point_inside(self, px, py) -> bool:
        diameter = min(self.width, self.height)
        cx, cy = self.x + diameter / 2, self.y + diameter / 2
        r = diameter / 2
        return ((px - cx) ** 2 + (py - cy) ** 2) <= r ** 2

    def clone(self) -> 'CircleElement':
        cloned = CircleElement(self.x, self.y, self.width, self.height, self.fill_color, self.stroke_color, self.stroke_width)
        cloned.is_selected = self.is_selected
        return cloned

    def to_dict(self) -> dict:
        return {
            "type": "Circle", "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "fill_color": self.fill_color, "stroke_color": self.stroke_color, "stroke_width": self.stroke_width
        }


class OvalElement(DrawingElement):
    """椭圆形元素"""
    def draw(self, canvas: tk.Canvas):
        canvas.create_oval(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=self.fill_color if self.fill_color else "", 
            outline=self.stroke_color, width=self.stroke_width
        )

    def is_point_inside(self, px, py) -> bool:
        cx, cy = self.x + self.width / 2, self.y + self.height / 2
        rx, ry = self.width / 2, self.height / 2
        if rx == 0 or ry == 0:
            return False
        return ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1.0

    def clone(self) -> 'OvalElement':
        cloned = OvalElement(self.x, self.y, self.width, self.height, self.fill_color, self.stroke_color, self.stroke_width)
        cloned.is_selected = self.is_selected
        return cloned

    def to_dict(self) -> dict:
        return {
            "type": "Oval", "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "fill_color": self.fill_color, "stroke_color": self.stroke_color, "stroke_width": self.stroke_width
        }


class TriangleElement(DrawingElement):
    """等腰三角形元素"""
    def draw(self, canvas: tk.Canvas):
        p1 = (self.x + self.width / 2, self.y)
        p2 = (self.x, self.y + self.height)
        p3 = (self.x + self.width, self.y + self.height)
        canvas.create_polygon(
            p1[0], p1[1], p2[0], p2[1], p3[0], p3[1],
            fill=self.fill_color if self.fill_color else "", 
            outline=self.stroke_color, width=self.stroke_width
        )

    def is_point_inside(self, px, py) -> bool:
        p1 = (self.x + self.width / 2, self.y)
        p2 = (self.x, self.y + self.height)
        p3 = (self.x + self.width, self.y + self.height)
        
        def sign(p1_val, p2_val, p3_val):
            return (p1_val[0] - p3_val[0]) * (p2_val[1] - p3_val[1]) - (p2_val[0] - p3_val[0]) * (p1_val[1] - p3_val[1])

        d1 = sign((px, py), p1, p2)
        d2 = sign((px, py), p2, p3)
        d3 = sign((px, py), p3, p1)

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)

    def clone(self) -> 'TriangleElement':
        cloned = TriangleElement(self.x, self.y, self.width, self.height, self.fill_color, self.stroke_color, self.stroke_width)
        cloned.is_selected = self.is_selected
        return cloned

    def to_dict(self) -> dict:
        return {
            "type": "Triangle", "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "fill_color": self.fill_color, "stroke_color": self.stroke_color, "stroke_width": self.stroke_width
        }


class LineElement(DrawingElement):
    """连接线元素"""
    def draw(self, canvas: tk.Canvas):
        canvas.create_line(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=self.stroke_color, width=self.stroke_width
        )

    def is_point_inside(self, px, py) -> bool:
        x1, y1 = self.x, self.y
        x2, y2 = self.x + self.width, self.y + self.height
        line_len = math.hypot(x2 - x1, y2 - y1)
        if line_len == 0:
            return math.hypot(px - x1, py - y1) < 8
        t = max(0.0, min(1.0, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_len ** 2)))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        return math.hypot(px - proj_x, py - proj_y) < 8

    def clone(self) -> 'LineElement':
        cloned = LineElement(self.x, self.y, self.width, self.height, self.fill_color, self.stroke_color, self.stroke_width)
        cloned.is_selected = self.is_selected
        return cloned

    def to_dict(self) -> dict:
        return {
            "type": "Line", "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "fill_color": self.fill_color, "stroke_color": self.stroke_color, "stroke_width": self.stroke_width
        }