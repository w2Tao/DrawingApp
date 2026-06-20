import tkinter as tk
from tkinter import ttk, messagebox

class DimensionDialog(tk.Toplevel):
    """
    属性控制对话框，用于修改图形的精确宽度与高度。
    """
    def __init__(self, parent, title, width, height):
        super().__init__(parent)
        self.title(title)
        self.geometry("260x160")
        self.resizable(False, False)
        
        self.transient(parent)  
        self.grab_set()         
        
        self.result = None
        
        x = parent.winfo_x() + (parent.winfo_width() - 260) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 160) // 2
        self.geometry(f"+{x}+{y}")
        
        lbl_w = ttk.Label(self, text="新宽度 (px):")
        lbl_w.pack(pady=(15, 2))
        self.ent_w = ttk.Entry(self, width=15)
        self.ent_w.insert(0, str(int(width)))
        self.ent_w.pack()
        
        lbl_h = ttk.Label(self, text="新高度 (px):")
        lbl_h.pack(pady=(5, 2))
        self.ent_h = ttk.Entry(self, width=15)
        self.ent_h.insert(0, str(int(height)))
        self.ent_h.pack()
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)
        
        btn_ok = tk.Button(btn_frame, text="确认", command=self.on_ok, width=8, bg="#e1e1e1", activebackground="#cccccc")
        btn_ok.pack(side=tk.LEFT, padx=5)
        btn_cancel = tk.Button(btn_frame, text="取消", command=self.on_cancel, width=8, bg="#e1e1e1", activebackground="#cccccc")
        btn_cancel.pack(side=tk.LEFT, padx=5)
        
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window()  
        
    def on_ok(self):
        try:
            w = int(self.ent_w.get())
            h = int(self.ent_h.get())
            if w <= 0 or h <= 0:
                raise ValueError
            self.result = (w, h)
            self.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入大于 0 的有效整数！", parent=self)
            
    def on_cancel(self):
        self.destroy()