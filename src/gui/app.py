import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
import json

from shapes.text import TextElement
from shapes.group import CombinedGroupElement
from factory.element_factory import ElementFactory
from commands.manager import CommandManager
from commands.actions import (
    AddCommand, DeleteCommand, TransformCommand, GroupCommand, UngroupCommand, LayerCommand
)
from gui.dialogs import DimensionDialog

class DrawingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("基础图形绘制软件")
        self.geometry("1280x720")
        
        # 初始化属性状态
        self.canvas_elements = []
        self.selected_elements = []
        self.clipboard = []  
        self.active_tool = "SELECT"  
        self.fill_color = "#ffffff"
        self.stroke_color = "#2c3e50"
        self.theme_mode = "LIGHT"  
        self.font_scale = 12
        
        # 实例化设计模式管理器
        self.command_manager = CommandManager(on_state_changed_callback=self.refresh_canvas)
        
        # 拖拽交互状态
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_action = None  
        self.temp_creation_element = None
        self.active_transform_cmd = None
        
        # 构建 UI 布局
        self.setup_ui_styles()
        self.create_menu()
        self.create_widgets()
        self.bind_events()
        self.apply_theme()

    def setup_ui_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建画布", command=self.new_canvas)
        file_menu.add_command(label="导入图形 (Load)", command=self.load_from_disk)
        file_menu.add_command(label="导出保存 (Save)", command=self.save_to_disk)
        file_menu.add_separator()
        file_menu.add_command(label="退出程序", command=self.quit)
        menubar.add_cascade(label="文件 (File)", menu=file_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="撤销 (Undo)", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="重做 (Redo)", accelerator="Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="复制 (Copy)", accelerator="Ctrl+C", command=self.copy_selection)
        edit_menu.add_command(label="粘贴 (Paste)", accelerator="Ctrl+V", command=self.paste_selection)
        edit_menu.add_command(label="删除 (Delete)", accelerator="Del", command=self.delete_selection)
        menubar.add_cascade(label="编辑 (Edit)", menu=edit_menu)
        
        self.config(menu=menubar)

    def create_widgets(self):
        # 顶端控制面板框架
        self.top_bar = ttk.Frame(self, padding=5)
        self.top_bar.pack(side=tk.TOP, fill=tk.X)

        # 撤销/重做
        self.btn_undo = ttk.Button(self.top_bar, text="Undo", command=self.undo, width=6)
        self.btn_undo.pack(side=tk.LEFT, padx=2)
        self.btn_redo = ttk.Button(self.top_bar, text="Redo", command=self.redo, width=6)
        self.btn_redo.pack(side=tk.LEFT, padx=2)

        ttk.Separator(self.top_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 层级管理
        self.btn_front = ttk.Button(self.top_bar, text="置顶", command=self.bring_to_front, width=6)
        self.btn_front.pack(side=tk.LEFT, padx=2)
        self.btn_back = ttk.Button(self.top_bar, text="置底", command=self.send_to_back, width=6)
        self.btn_back.pack(side=tk.LEFT, padx=2)

        ttk.Separator(self.top_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 颜色修改器
        self.btn_fill = tk.Button(self.top_bar, text="填充色", bg=self.fill_color, command=self.choose_fill_color, width=8, relief=tk.GROOVE)
        self.btn_fill.pack(side=tk.LEFT, padx=2)
        self.btn_transparent = ttk.Button(self.top_bar, text="透明背景", command=self.set_fill_transparent)
        self.btn_transparent.pack(side=tk.LEFT, padx=2)
        self.btn_stroke = tk.Button(self.top_bar, text="描边/文字色", bg=self.stroke_color, fg="white", command=self.choose_stroke_color, width=10, relief=tk.GROOVE)
        self.btn_stroke.pack(side=tk.LEFT, padx=2)

        ttk.Separator(self.top_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 文本框描述属性修改
        ttk.Label(self.top_bar, text="文本内容:").pack(side=tk.LEFT, padx=2)
        self.text_entry = ttk.Entry(self.top_bar, width=15)
        self.text_entry.pack(side=tk.LEFT, padx=2)
        self.btn_apply_text = ttk.Button(self.top_bar, text="设置文本", command=self.apply_text_to_selection)
        self.btn_apply_text.pack(side=tk.LEFT, padx=2)

        ttk.Separator(self.top_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 组合与拆解控制
        self.btn_group = ttk.Button(self.top_bar, text="组合", command=self.group_selection, width=6)
        self.btn_group.pack(side=tk.LEFT, padx=2)
        self.btn_ungroup = ttk.Button(self.top_bar, text="打散", command=self.ungroup_selection, width=6)
        self.btn_ungroup.pack(side=tk.LEFT, padx=2)
        self.btn_delete = ttk.Button(self.top_bar, text="删除", command=self.delete_selection, width=6)
        self.btn_delete.pack(side=tk.LEFT, padx=2)

        # 个性化界面切换与字体微调
        self.btn_theme = ttk.Button(self.top_bar, text="暗黑模式", command=self.toggle_theme_mode)
        self.btn_theme.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(self.top_bar, text="文本字号:").pack(side=tk.RIGHT, padx=2)
        self.font_spinbox = ttk.Spinbox(self.top_bar, from_=8, to=72, width=3, command=self.on_font_scale_changed)
        self.font_spinbox.set(self.font_scale)
        self.font_spinbox.pack(side=tk.RIGHT, padx=2)
        self.font_spinbox.bind("<Return>", lambda e: self.on_font_scale_changed())
        self.font_spinbox.bind("<FocusOut>", lambda e: self.on_font_scale_changed())

        # 底部状态条 (提前渲染到窗口最下方，保障画布区域的完整性)
        self.status_bar = ttk.Label(self, text="提示: 鼠标拖拽可绘制图形，支持层级置顶/置底。空文本框失去选择焦点时会自动清除", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 侧边栏工具架
        self.sidebar = ttk.Frame(self, padding=5)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(self.sidebar, text="绘图工具", font=("Arial", 11, "bold")).pack(pady=5)
        
        self.tools = [
            ("选择工具 (Select)", "SELECT"),
            ("方框矩形 (Rect)", "Rectangle"),
            ("正圆元素 (Circle)", "Circle"),
            ("椭圆元素 (Oval)", "Oval"),
            ("三角形 (Triangle)", "Triangle"),
            ("连接线 (Line)", "Line"),
            ("文本框 (Text)", "Text")
        ]
        self.tool_buttons = {}
        for text, tool_id in self.tools:
            btn = ttk.Button(self.sidebar, text=text, command=lambda tid=tool_id: self.select_tool(tid))
            btn.pack(fill=tk.X, pady=2, ipady=4)
            self.tool_buttons[tool_id] = btn

        # 主工作画布框架
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#ffffff", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.select_tool("SELECT")

    def bind_events(self):
        # 鼠标画布事件绑定
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # 跨平台右键点击事件绑定
        self.canvas.bind("<Button-3>", self.on_right_click)  # Windows / Linux
        self.canvas.bind("<Button-2>", self.on_right_click)  # MacOS

        # 系统级快捷键绑定
        self.bind_all("<Control-z>", lambda e: self.undo())
        self.bind_all("<Control-y>", lambda e: self.redo())
        self.bind_all("<Control-c>", lambda e: self.copy_selection())
        self.bind_all("<Control-v>", lambda e: self.paste_selection())
        self.bind_all("<Delete>", lambda e: self.delete_selection())

    def deselect_element(self, el):
        """取消选中某个元素，如果该元素是内容为空的独立文本框，则直接将其销毁"""
        el.is_selected = False
        if isinstance(el, TextElement) and not el.text.strip():
            if el in self.canvas_elements:
                self.canvas_elements.remove(el)

    def on_canvas_press(self, event):
        px, py = event.x, event.y
        self.drag_start_x = px
        self.drag_start_y = py

        if self.active_tool == "SELECT":
            handle_clicked = False
            for el in reversed(self.selected_elements):
                hx = el.x + el.width
                hy = el.y + el.height
                if hx - 8 <= px <= hx + 8 and hy - 8 <= py <= hy + 8:
                    handle_clicked = True
                    self.drag_action = "RESIZE"
                    break
            
            if handle_clicked:
                self.active_transform_cmd = TransformCommand(self.selected_elements)
                return

            hit_element = None
            for el in reversed(self.canvas_elements):
                if el.is_point_inside(px, py):
                    hit_element = el
                    break

            if hit_element:
                is_shift = bool(event.state & 0x0001)
                if is_shift:
                    if hit_element in self.selected_elements:
                        self.selected_elements.remove(hit_element)
                        self.deselect_element(hit_element)
                    else:
                        self.selected_elements.append(hit_element)
                        hit_element.is_selected = True
                else:
                    if hit_element not in self.selected_elements:
                        self.clear_all_selection()
                        self.selected_elements = [hit_element]
                        hit_element.is_selected = True
                
                self.drag_action = "MOVE"
                self.active_transform_cmd = TransformCommand(self.selected_elements)
            else:
                self.clear_all_selection()
                self.drag_action = "BOX_SELECT"
            
            self.refresh_canvas()
        else:
            self.drag_action = "CREATE"
            self.temp_creation_element = ElementFactory.create_element(
                self.active_tool, px, py, 1, 1,
                fill_color=self.fill_color if self.active_tool != "Text" else "",
                stroke_color=self.stroke_color
            )

    def on_canvas_drag(self, event):
        px, py = event.x, event.y
        dx = px - self.drag_start_x
        dy = py - self.drag_start_y
        
        if self.drag_action == "MOVE":
            for el in self.selected_elements:
                el.move(dx, dy)
            self.drag_start_x = px
            self.drag_start_y = py
            self.refresh_canvas()

        elif self.drag_action == "RESIZE":
            for el in self.selected_elements:
                el.resize(dx, dy)
                if isinstance(el, CombinedGroupElement):
                    el.recalculate_bounds()
            self.drag_start_x = px
            self.drag_start_y = py
            self.refresh_canvas()

        elif self.drag_action == "BOX_SELECT":
            self.refresh_canvas()
            self.canvas.create_rectangle(
                self.drag_start_x, self.drag_start_y, px, py,
                outline="#4a90e2", dash=(4, 4), width=1
            )

        elif self.drag_action == "CREATE" and self.temp_creation_element:
            new_w = px - self.temp_creation_element.x
            new_h = py - self.temp_creation_element.y
            
            if new_w >= 0:
                self.temp_creation_element.width = max(2, new_w)
            if new_h >= 0:
                self.temp_creation_element.height = max(2, new_h)
            
            self.refresh_canvas()
            self.temp_creation_element.draw(self.canvas)

    def on_canvas_release(self, event):
        if self.drag_action in ("MOVE", "RESIZE") and self.active_transform_cmd:
            self.active_transform_cmd.record_after_state()
            self.command_manager.execute_command(self.active_transform_cmd)
            self.active_transform_cmd = None

        elif self.drag_action == "BOX_SELECT":
            x1 = min(self.drag_start_x, event.x)
            y1 = min(self.drag_start_y, event.y)
            x2 = max(self.drag_start_x, event.x)
            y2 = max(self.drag_start_y, event.y)
            
            if (x2 - x1) > 4 or (y2 - y1) > 4:
                for el in self.canvas_elements:
                    el_cx = el.x + el.width / 2
                    el_cy = el.y + el.height / 2
                    if x1 <= el_cx <= x2 and y1 <= el_cy <= y2:
                        el.is_selected = True
                        if el not in self.selected_elements:
                            self.selected_elements.append(el)
            self.refresh_canvas()

        elif self.drag_action == "CREATE" and self.temp_creation_element:
            # 如果是文本框且未拖拽，赋予默认的尺寸
            if isinstance(self.temp_creation_element, TextElement) and \
               self.temp_creation_element.width < 10 and self.temp_creation_element.height < 10:
                self.temp_creation_element.width = 120
                self.temp_creation_element.height = 35

            cmd = AddCommand(self.canvas_elements, self.temp_creation_element)
            self.command_manager.execute_command(cmd)
            self.select_tool("SELECT")
            
            self.clear_all_selection()
            self.selected_elements = [self.temp_creation_element]
            self.temp_creation_element.is_selected = True
            self.temp_creation_element = None
            self.refresh_canvas()

        self.drag_action = None

    def select_tool(self, tool_id):
        self.active_tool = tool_id
        for tid, btn in self.tool_buttons.items():
            if tid == tool_id:
                btn.configure(style="Accent.TButton")
            else:
                btn.configure(style="TButton")

    def refresh_canvas(self):
        self.canvas.delete("all")
        for el in self.canvas_elements:
            el.draw(self.canvas)
            if el.is_selected:
                self.draw_selection_border(el)
        self.update_properties_ui()

    def draw_selection_border(self, el):
        self.canvas.create_rectangle(
            el.x, el.y, el.x + el.width, el.y + el.height,
            outline="#4a90e2", dash=(2, 2), width=1
        )
        hx = el.x + el.width
        hy = el.y + el.height
        self.canvas.create_rectangle(
            hx - 4, hy - 4, hx + 4, hy + 4,
            fill="#4a90e2", outline="#ffffff"
        )

    def clear_all_selection(self):
        for el in list(self.selected_elements):
            self.deselect_element(el)
        self.selected_elements.clear()

    def update_properties_ui(self):
        """同步显示选中的文本属性"""
        text_els = [el for el in self.selected_elements if isinstance(el, TextElement)]
        if text_els:
            el = text_els[0]
            if self.focus_get() != self.text_entry:
                self.text_entry.delete(0, tk.END)
                self.text_entry.insert(0, el.text)
            self.font_spinbox.set(int(el.font_size))
        else:
            if self.focus_get() != self.text_entry:
                self.text_entry.delete(0, tk.END)

    def bring_to_front(self):
        """置顶层级"""
        if not self.selected_elements:
            return
        cmd = LayerCommand(self.canvas_elements, self.selected_elements, "FRONT")
        self.command_manager.execute_command(cmd)

    def send_to_back(self):
        """置底层级"""
        if not self.selected_elements:
            return
        cmd = LayerCommand(self.canvas_elements, self.selected_elements, "BACK")
        self.command_manager.execute_command(cmd)

    def on_right_click(self, event):
        if len(self.selected_elements) > 1:
            self.status_bar.config(text="提示: 选中多个图形时不支持右键尺寸调整")
            return

        px, py = event.x, event.y
        hit_el = None
        for el in reversed(self.canvas_elements):
            if el.is_point_inside(px, py):
                hit_el = el
                break

        if hit_el:
            if isinstance(hit_el, CombinedGroupElement):
                self.status_bar.config(text="提示: 组合图形不支持通过右键属性框进行尺寸微调")
                return
            
            if isinstance(hit_el, TextElement):
                self.status_bar.config(text="提示: 文本框图形不支持通过右键对话框修改尺寸")
                return
            
            self.clear_all_selection()
            self.selected_elements = [hit_el]
            hit_el.is_selected = True
            self.refresh_canvas()
            
            self.pop_dimension_dialog(hit_el)

    def pop_dimension_dialog(self, el):
        dialog = DimensionDialog(self, "修改图形尺寸", el.width, el.height)
        if dialog.result:
            new_w, new_h = dialog.result
            cmd = TransformCommand([el])
            el.width = new_w
            el.height = new_h
            cmd.record_after_state()
            self.command_manager.execute_command(cmd)

    def copy_selection(self):
        if not self.selected_elements:
            self.status_bar.config(text="提示: 未选中任何图形，无法复制")
            return
        self.clipboard = [el.clone() for el in self.selected_elements]
        self.status_bar.config(text=f"提示: 已复制 {len(self.clipboard)} 个图形")

    def paste_selection(self):
        if not self.clipboard:
            self.status_bar.config(text="提示: 剪切板为空")
            return

        new_copies = []
        for el in self.clipboard:
            cloned = el.clone()
            cloned.move(25, 25)
            if isinstance(cloned, CombinedGroupElement):
                cloned.recalculate_bounds()
            new_copies.append(cloned)

        cmd = AddCommand(self.canvas_elements, new_copies)
        self.command_manager.execute_command(cmd)

        self.clear_all_selection()
        for c in new_copies:
            c.is_selected = True
            self.selected_elements.append(c)

        self.clipboard = [el.clone() for el in new_copies]
        self.refresh_canvas()

    def delete_selection(self):
        if self.selected_elements:
            cmd = DeleteCommand(self.canvas_elements, self.selected_elements)
            self.command_manager.execute_command(cmd)
            self.selected_elements.clear()
            self.refresh_canvas()
            self.status_bar.config(text="提示: 已删除选中图形")
        else:
            self.status_bar.config(text="提示: 未选中任何图形，无法执行删除")

    def apply_text_to_selection(self):
        """将输入文本应用到选中的独立文本框中"""
        new_text = self.text_entry.get()
        text_els = [el for el in self.selected_elements if isinstance(el, TextElement)]
        if not text_els:
            messagebox.showinfo("提示", "请先选择独立文本框图形以设置文本。")
            return
        
        cmd = TransformCommand(text_els)
        for el in text_els:
            el.text = new_text
        cmd.record_after_state()
        self.command_manager.execute_command(cmd)

    def on_font_scale_changed(self):
        """当调整顶部字号时，针对当前选中的独立文本框生效"""
        try:
            val = int(self.font_spinbox.get())
        except ValueError:
            return
        
        text_els = [el for el in self.selected_elements if isinstance(el, TextElement)]
        if text_els:
            cmd = TransformCommand(text_els)
            for el in text_els:
                el.font_size = val
            cmd.record_after_state()
            self.command_manager.execute_command(cmd)

    def group_selection(self):
        if len(self.selected_elements) < 2:
            messagebox.showwarning("操作受限", "必须多选两个以上的图形才能进行组合。")
            return
        
        cmd = GroupCommand(self.canvas_elements, self.selected_elements)
        self.command_manager.execute_command(cmd)
        
        self.selected_elements = [cmd.group]
        self.refresh_canvas()

    def ungroup_selection(self):
        groups = [el for el in self.selected_elements if isinstance(el, CombinedGroupElement)]
        if not groups:
            messagebox.showwarning("操作受限", "选中对象不包含任何组合图形。")
            return
        
        for g in groups:
            cmd = UngroupCommand(self.canvas_elements, g)
            self.command_manager.execute_command(cmd)
            self.selected_elements.remove(g)
            self.deselect_element(g)
            self.selected_elements.extend(cmd.children)
            
        self.refresh_canvas()

    def save_to_disk(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Vector Data", "*.json")])
        if not file_path:
            return
        
        serialized_list = [el.to_dict() for el in self.canvas_elements]
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serialized_list, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("成功", f"文件已保存至:\n{file_path}")
        except Exception as e:
            messagebox.showerror("写入错误", f"无法写入文件:\n{str(e)}")

    def load_from_disk(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Vector Data", "*.json")])
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            loaded_elements = [ElementFactory.from_dict(item) for item in raw_data]
            
            self.canvas_elements.clear()
            self.selected_elements.clear()
            self.command_manager.reset()
            
            self.canvas_elements = loaded_elements
            self.refresh_canvas()
            self.status_bar.config(text=f"已载入文件: {file_path}")
        except Exception as e:
            messagebox.showerror("加载失败", f"文件格式可能已损坏:\n{str(e)}")

    def new_canvas(self):
        if messagebox.askyesno("确认", "该操作将清空画布，确定继续？"):
            self.canvas_elements.clear()
            self.selected_elements.clear()
            self.command_manager.reset()
            self.refresh_canvas()

    def choose_fill_color(self):
        initial = self.fill_color if self.fill_color else "#ffffff"
        color = colorchooser.askcolor(initial, title="选择填充色")
        if color[1]:
            self.fill_color = color[1]
            self.btn_fill.config(bg=self.fill_color, text="填充色")
            if self.selected_elements:
                cmd = TransformCommand(self.selected_elements)
                for el in self.selected_elements:
                    el.fill_color = self.fill_color
                cmd.record_after_state()
                self.command_manager.execute_command(cmd)

    def set_fill_transparent(self):
        self.fill_color = ""
        self.btn_fill.config(bg="#f0f0f0", text="透明")
        if self.selected_elements:
            cmd = TransformCommand(self.selected_elements)
            for el in self.selected_elements:
                el.fill_color = ""
            cmd.record_after_state()
            self.command_manager.execute_command(cmd)

    def choose_stroke_color(self):
        color = colorchooser.askcolor(self.stroke_color, title="选择描边与文字颜色")
        if color[1]:
            self.stroke_color = color[1]
            fg = "white" if self.is_color_dark(self.stroke_color) else "black"
            self.btn_stroke.config(bg=self.stroke_color, fg=fg)
            if self.selected_elements:
                cmd = TransformCommand(self.selected_elements)
                for el in self.selected_elements:
                    el.stroke_color = self.stroke_color
                cmd.record_after_state()
                self.command_manager.execute_command(cmd)

    def is_color_dark(self, hex_color) -> bool:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return luminance < 0.5
        return False

    def toggle_theme_mode(self):
        if self.theme_mode == "LIGHT":
            self.theme_mode = "DARK"
            self.btn_theme.config(text="亮白模式")
        else:
            self.theme_mode = "LIGHT"
            self.btn_theme.config(text="暗黑模式")
        self.apply_theme()

    def apply_theme(self):
        if self.theme_mode == "LIGHT":
            canvas_bg = "#fcfcfc"
            panel_bg = "#f0f0f0"
            text_color = "#333333"
            self.canvas.config(bg=canvas_bg, highlightbackground="#dcdcdc")
        else:
            canvas_bg = "#252627"
            panel_bg = "#323233"
            text_color = "#ffffff"
            self.canvas.config(bg=canvas_bg, highlightbackground="#111213")

        self.style.configure("TFrame", background=panel_bg)
        self.style.configure("TLabel", background=panel_bg, foreground=text_color)
        self.top_bar.config(style="TFrame")
        self.sidebar.config(style="TFrame")
        self.canvas_frame.config(style="TFrame")
        self.refresh_canvas()

    def undo(self):
        self.command_manager.undo()

    def redo(self):
        self.command_manager.redo()