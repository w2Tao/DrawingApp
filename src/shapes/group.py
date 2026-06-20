import tkinter as tk
from .base import DrawingElement

class CombinedGroupElement(DrawingElement):
    """
    组合图形容器，支持嵌套组合、移动、缩放和克隆。
    (组合模式)
    """
    def __init__(self, children=None):
        super().__init__(0, 0, 0, 0)
        self.children = children if children else []
        self.recalculate_bounds()

    def recalculate_bounds(self):
        if not self.children:
            self.x, self.y, self.width, self.height = 0, 0, 0, 0
            return
        
        xs = [c.x for c in self.children] + [c.x + c.width for c in self.children]
        ys = [c.y for c in self.children] + [c.y + c.height for c in self.children]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        self.x = min_x
        self.y = min_y
        self.width = max_x - min_x
        self.height = max_y - min_y

    def draw(self, canvas: tk.Canvas):
        for child in self.children:
            child.draw(canvas)
        if self.is_selected:
            canvas.create_rectangle(
                self.x, self.y, self.x + self.width, self.y + self.height,
                outline="#4a90e2", dash=(4, 4), width=1
            )

    def is_point_inside(self, px, py) -> bool:
        return any(child.is_point_inside(px, py) for child in self.children)

    def move(self, dx, dy):
        super().move(dx, dy)
        for child in self.children:
            child.move(dx, dy)

    def resize(self, dw, dh):
        old_w, old_h = self.width, self.height
        super().resize(dw, dh)
        new_w, new_h = self.width, self.height
        
        factor_x = (new_w / old_w) if old_w > 0 else 1.0
        factor_y = (new_h / old_h) if old_h > 0 else 1.0
        
        for child in self.children:
            rel_x = child.x - self.x
            rel_y = child.y - self.y
            
            child.x = self.x + rel_x * factor_x
            child.y = self.y + rel_y * factor_y
            child.width *= factor_x
            child.height *= factor_y

        self.recalculate_bounds()

    def clone(self) -> 'CombinedGroupElement':
        cloned_children = [child.clone() for child in self.children]
        group = CombinedGroupElement(cloned_children)
        group.x = self.x
        group.y = self.y
        group.width = self.width
        group.height = self.height
        group.is_selected = self.is_selected
        return group

    def to_dict(self) -> dict:
        return {
            "type": "Group",
            "children": [child.to_dict() for child in self.children]
        }