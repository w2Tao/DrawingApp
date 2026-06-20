import copy
from .base import Command
from shapes.group import CombinedGroupElement
from factory.element_factory import ElementFactory

class AddCommand(Command):
    """添加图形命令"""
    def __init__(self, elements_list, element):
        self.elements_list = elements_list
        self.elements = element if isinstance(element, list) else [element]

    def execute(self):
        for el in self.elements:
            if el not in self.elements_list:
                self.elements_list.append(el)

    def undo(self):
        for el in self.elements:
            if el in self.elements_list:
                self.elements_list.remove(el)


class DeleteCommand(Command):
    """删除图形命令"""
    def __init__(self, elements_list, elements_to_delete):
        self.elements_list = elements_list
        self.targets = list(elements_to_delete)

    def execute(self):
        for el in self.targets:
            if el in self.elements_list:
                self.elements_list.remove(el)

    def undo(self):
        for el in self.targets:
            if el not in self.elements_list:
                self.elements_list.append(el)


class TransformCommand(Command):
    """处理移动、尺寸调整、字体和文本内容修改的快照状态记录"""
    def __init__(self, elements):
        self.elements = list(elements)
        self.before_states = [copy.deepcopy(el.to_dict()) for el in self.elements]
        self.after_states = []

    def record_after_state(self):
        self.after_states = [copy.deepcopy(el.to_dict()) for el in self.elements]

    def execute(self):
        if self.after_states:
            self._apply_states(self.after_states)

    def undo(self):
        self._apply_states(self.before_states)

    def _apply_states(self, states):
        for el, state in zip(self.elements, states):
            if state["type"] == "Group":
                temp = ElementFactory.from_dict(state)
                el.children = temp.children
                el.x, el.y, el.width, el.height = temp.x, temp.y, temp.width, temp.height
            elif state["type"] == "Text":
                el.x = state["x"]
                el.y = state["y"]
                el.width = state["width"]
                el.height = state["height"]
                el.text = state["text"]
                el.fill_color = state["fill_color"]
                el.stroke_color = state["stroke_color"]
                el.font_size = state.get("font_size", 12)
            else:
                el.x = state["x"]
                el.y = state["y"]
                el.width = state["width"]
                el.height = state["height"]
                el.fill_color = state["fill_color"]
                el.stroke_color = state["stroke_color"]
                el.stroke_width = state["stroke_width"]


class GroupCommand(Command):
    """组合命令"""
    def __init__(self, elements_list, targets):
        self.elements_list = elements_list
        self.targets = list(targets)
        self.group = None

    def execute(self):
        if not self.group:
            self.group = CombinedGroupElement(self.targets)
        for el in self.targets:
            if el in self.elements_list:
                self.elements_list.remove(el)
                el.is_selected = False
        self.elements_list.append(self.group)
        self.group.is_selected = True

    def undo(self):
        if self.group in self.elements_list:
            self.elements_list.remove(self.group)
        for el in self.targets:
            self.elements_list.append(el)
            el.is_selected = True
        self.group.is_selected = False


class UngroupCommand(Command):
    """取消组合命令"""
    def __init__(self, elements_list, group):
        self.elements_list = elements_list
        self.group = group
        self.children = list(group.children)

    def execute(self):
        if self.group in self.elements_list:
            self.elements_list.remove(self.group)
        for child in self.children:
            self.elements_list.append(child)
            child.is_selected = True
        self.group.is_selected = False

    def undo(self):
        for child in self.children:
            if child in self.elements_list:
                self.elements_list.remove(child)
                child.is_selected = False
        self.elements_list.append(self.group)
        self.group.is_selected = True


class LayerCommand(Command):
    """图形层级（Z-Index）操作命令"""
    def __init__(self, elements_list, targets, action="FRONT"):
        self.elements_list = elements_list
        self.targets = list(targets)
        self.action = action
        self.old_order = list(elements_list)
        self.new_order = []

    def execute(self):
        if not self.new_order:
            remaining = [el for el in self.elements_list if el not in self.targets]
            sorted_targets = [el for el in self.old_order if el in self.targets]
            if self.action == "FRONT":
                self.new_order = remaining + sorted_targets
            elif self.action == "BACK":
                self.new_order = sorted_targets + remaining
        
        self.elements_list.clear()
        self.elements_list.extend(self.new_order)

    def undo(self):
        self.elements_list.clear()
        self.elements_list.extend(self.old_order)