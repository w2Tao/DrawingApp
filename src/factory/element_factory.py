from shapes.base import DrawingElement
from shapes.geometric import RectangleElement, CircleElement, OvalElement, TriangleElement, LineElement
from shapes.text import TextElement
from shapes.group import CombinedGroupElement

class ElementFactory:
    """创建具体图形及根据反序列化加载图形 (工厂模式)"""
    @staticmethod
    def create_element(el_type: str, x: float, y: float, w: float, h: float, **kwargs) -> DrawingElement:
        if el_type == "Rectangle":
            return RectangleElement(x, y, w, h, **kwargs)
        elif el_type == "Circle":
            return CircleElement(x, y, w, h, **kwargs)
        elif el_type == "Oval":
            return OvalElement(x, y, w, h, **kwargs)
        elif el_type == "Triangle":
            return TriangleElement(x, y, w, h, **kwargs)
        elif el_type == "Line":
            return LineElement(x, y, w, h, **kwargs)
        elif el_type == "Text":
            text_val = kwargs.pop("text", "")
            font_size = kwargs.pop("font_size", 12)
            return TextElement(x, y, w, h, text=text_val, font_size=font_size, **kwargs)
        else:
            raise ValueError(f"Unknown design type: {el_type}")
    
    @staticmethod
    def from_dict(data: dict) -> DrawingElement:
        el_type = data.get("type")
        if el_type == "Group":
            children = [ElementFactory.from_dict(c) for c in data.get("children", [])]
            group = CombinedGroupElement(children)
            return group
        elif el_type == "Text":
            return TextElement(
                x=data.get("x", 0), y=data.get("y", 0),
                width=data.get("width", 100), height=data.get("height", 30),
                text=data.get("text", ""),
                fill_color=data.get("fill_color", ""),
                stroke_color=data.get("stroke_color", "#000000"),
                font_size=data.get("font_size", 12),
                stroke_width=data.get("stroke_width", 1)
            )
        else:
            return ElementFactory.create_element(
                el_type=el_type,
                x=data.get("x", 0), y=data.get("y", 0),
                w=data.get("width", 50), h=data.get("height", 50),
                fill_color=data.get("fill_color", "#ffffff"),
                stroke_color=data.get("stroke_color", "#000000"),
                stroke_width=data.get("stroke_width", 2)
            )