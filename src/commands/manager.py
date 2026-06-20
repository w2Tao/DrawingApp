from .base import Command

class CommandManager:
    """管理撤销与重做的命令栈"""
    def __init__(self, on_state_changed_callback=None):
        self.undo_stack = []
        self.redo_stack = []
        self.callback = on_state_changed_callback

    def execute_command(self, cmd: Command):
        cmd.execute()
        self.undo_stack.append(cmd)
        self.redo_stack.clear()
        if self.callback:
            self.callback()

    def undo(self):
        if self.undo_stack:
            cmd = self.undo_stack.pop()
            cmd.undo()
            self.redo_stack.append(cmd)
            if self.callback:
                self.callback()

    def redo(self):
        if self.redo_stack:
            cmd = self.redo_stack.pop()
            cmd.execute()
            self.undo_stack.append(cmd)
            if self.callback:
                self.callback()

    def reset(self):
        self.undo_stack.clear()
        self.redo_stack.clear()