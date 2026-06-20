# 基础图形绘制软件实验报告

## 摘要
本实验设计并开发了一个基于面向对象编程语言（Python）的基础图形绘制软件，系统通过 Tkinter 实现图形化用户交互（GUI）。为满足高内聚、低耦合的软件工程设计标准，本项目在架构中运用了工厂方法、组合、原型、命令及备忘录等设计模式。本报告将详细阐述系统需求分析、分层架构设计、设计模式具体应用、核心算法实现以及测试验证，并对本系统的设计进行客观评价。

---

## 一、 需求分析与模块化重构目标

### 1.1 核心需求
根据作业硬性指标，本系统需要提供以下功能：
1.  **基础图形绘制**：三角形、矩形、圆形、椭圆、连接线及文本框。
2.  **元素基础操作**：图形选中、多选、克隆复制、多图层叠放、文字描述应用。
3.  **图形组合（Group）**：多图形的打包、嵌套整体拖拽及克隆。
4.  **历史记录管理**：支持多步连续撤销（Undo）与重做（Redo）。
5.  **数据本地持久化**：自定义矢量格式的导出与加载恢复。

### 1.2 重构目标
原始 `main.py` 采用单文件编写，各类图形的定义、业务命令、文件读写及 GUI 视窗逻辑均高度交织。为了消除职责混乱，提高系统代码的鲁棒性，本项目将其重构为 **11 个独立的类模块**，并按职责划分为 `shapes`（模型域）、`factory`（创建域）、`commands`（控制域）、`gui`（视图域）等包。

---

## 二、 系统架构设计与模块划分

重构后的多文件系统遵循经典的 **MVC（模型-视图-控制器）** 模式变体。其核心调用关系如下：

```text
+------------------+         (触发事件)         +--------------------+
|  GUI 视图层      | ------------------------> |  Commands 控制层   |
|  (gui.app.App)   | <------------------------ |  (commands.actions)|
+------------------+     (数据更新，重绘)      +--------------------+
         |                                               |
         | (通过工厂加载)                                 | (操作元素)
         v                                               v
+-----------------------+                      +---------------------+
|  Factory 工厂层       |                      |  Shapes 模型层      |
|  (element_factory.py) | -------------------> |  (base, geometric)  |
+-----------------------+                      +---------------------+
```

*   **模型层（Shapes）**：维护图形实体的数据状态（坐标、大小、颜色、文本、选中态等）并实现基本的自绘逻辑，不包含任何 UI 布局代码。
*   **创建层（Factory）**：负责对象的构建逻辑，解除客户端与具体子类之间的直接耦合。
*   **控制与命令层（Commands）**：将所有对图形列表的写操作进行“对象化封装”，实现状态快照的管理。
*   **视图层（GUI）**：捕捉用户键鼠操作，转换为具体的业务命令并分发。

---

## 三、 设计模式应用分析

系统内深度融入了 5 种设计模式，以下阐述这些模式在代码中的应用及设计考量。

### 3.1 原型模式 (Prototype Pattern)
*   **应用场景**：基础功能 3（图形克隆复制）。
*   **设计逻辑**：
    在 `DrawingElement` 基类中声明抽象接口 `clone()`。每个具体图形实体（如 `RectangleElement`、`TextElement`）均重写该方法，通过调用构造函数或进行成员属性拷贝来返回一个全新的副本。
*   **代码体现**：
    ```python
    # shapes/base.py
    @abstractmethod
    def clone(self) -> 'DrawingElement': pass

    # shapes/geometric.py 中的具体实现
    def clone(self) -> 'RectangleElement':
        cloned = RectangleElement(self.x, self.y, self.width, self.height, self.fill_color, self.stroke_color, self.stroke_width)
        cloned.is_selected = self.is_selected
        return cloned
    ```

### 3.2 组合模式 (Composite Pattern)
*   **应用场景**：基础功能 4（多图形组合打包作为一个整体移动或克隆）。
*   **设计逻辑**：
    `CombinedGroupElement` 同样继承自 `DrawingElement` 基类，表现为“容器对象”，它在内部维护一个 `List[DrawingElement]`。当外部调用其 `move()`、`resize()`、`draw()` 或 `clone()` 方法时，它将操作递归地分发给其所持有的所有子图形。如此一来，系统客户端无需区分面对的是单体图形还是组合体，实现了“一致性对待”。
*   **代码体现**：
    ```python
    # shapes/group.py
    class CombinedGroupElement(DrawingElement):
        def __init__(self, children=None):
            super().__init__(0, 0, 0, 0)
            self.children = children if children else []
            self.recalculate_bounds()

        def move(self, dx, dy):
            super().move(dx, dy)
            for child in self.children:
                child.move(dx, dy)
    ```

### 3.3 工厂方法模式 (Factory Method Pattern)
*   **应用场景**：基础功能 1、扩展功能 5（动态创建图形和反序列化重建图形对象）。
*   **设计逻辑**：
    由 `ElementFactory` 类提供静态方法 `create_element()` 与 `from_dict()`。前者根据客户端工具栏下发的字符串标示（如 "Triangle"）动态组装具体对象；后者接受解析自 JSON 的属性字典，生成与之匹配的类实例，隐藏了具体的实例化和参数组装细节。

### 3.4 命令模式 (Command Pattern)
*   **应用场景**：基础功能 5、扩展功能 4（多步撤销与重做）。
*   **设计逻辑**：
    将每个导致画布状态改变的操作抽象为 `Command` 接口实现类：
    *   `AddCommand`：封装添加图形逻辑。
    *   `DeleteCommand`：封装删除图形逻辑。
    *   `TransformCommand`：通过快照方式，保存移动/缩放/修改属性前后的参数状态。
    *   `GroupCommand` / `UngroupCommand` / `LayerCommand`：处理组合及图层调整。
    由 `CommandManager` 统一管理 `undo_stack` 和 `redo_stack` 两个历史记录栈。
*   **代码体现**：
    ```python
    # commands/actions.py 中 TransformCommand 实现快照恢复
    class TransformCommand(Command):
        def __init__(self, elements):
            self.elements = list(elements)
            self.before_states = [copy.deepcopy(el.to_dict()) for el in self.elements] # 记录操作前状态
            self.after_states = []

        def record_after_state(self):
            self.after_states = [copy.deepcopy(el.to_dict()) for el in self.elements] # 记录操作后状态

        def undo(self):
            self._apply_states(self.before_states) # 撤销恢复
    ```

### 3.5 备忘录模式 / 状态序列化 (Memento / Serialization)
*   **应用场景**：扩展功能 5（图形状态导出与加载恢复）。
*   **设计逻辑**：
    每个图形实体均具备 `to_dict()` 接口（即备忘录的导出机制），用于生成纯粹的属性字典。在保存时，所有图形组成的数组被转为 JSON 字符串并写入硬盘。读取时，工厂读取这些字典并重新构造出和先前完全一致的对象树。

---

## 四、 核心算法与关键细节实现

### 4.1 几何相交性检测（Hit Testing）
为了支持鼠标选中检测，各图形需要提供精确的相交性判断方法 `is_point_inside(px, py)`：
*   **等腰三角形**：通过“同侧法（Sign test）”计算点是否处于三角形三条边界线所夹的相同区域内部。
*   **椭圆**：应用椭圆的标准代数方程求解：
    $$\frac{(p_x - c_x)^2}{r_x^2} + \frac{(p_y - c_y)^2}{r_y^2} \le 1.0$$
*   **连接线**：计算点到有限长度线段投影的垂直距离，若距离小于 8 像素则判定为“击中”。

### 4.2 组合嵌套尺寸等比缩放
在对组合图形整体调整尺寸时，由于子图形相对于组合体边界有不同的偏移，必须进行等比例几何投影变换：
1. 记录缩放前后组合包围盒的相对宽高比例系数 `factor_x` 和 `factor_y`。
2. 每一个子图形根据该系数重新计算其局部坐标与长宽：
   $$x_{\text{child\_new}} = x_{\text{group}} + (x_{\text{child}} - x_{\text{group}}) \times factor_x$$
   $$\text{width}_{\text{child\_new}} = \text{width}_{\text{child}} \times factor_x$$

---

## 五、 测试验证

在系统重构完成后，通过以下场景方案对各功能模块进行了手动的系统集成测试：

| 测试场景 | 操作步骤 | 预期效果 | 实测结果 |
| :--- | :--- | :--- | :--- |
| **图形绘制与多选** | 1. 绘制矩形、三角形、圆形。<br>2. 按 Shift 加选全部。<br>3. 框选全部。 | 所有图形外周出现蓝色选中虚线，右下角控制点正常显示。 | 符合预期 |
| **组合克隆** | 1. 多选三个不同几何体并点击“组合”。<br>2. 拖拽、缩放。<br>3. 复制并粘贴。 | 组合作为一个整体移动缩放；复制出的新组合与原组合完全独立。 | 符合预期 |
| **历史栈回滚** | 1. 绘制一个矩形并移动它。<br>2. 按 `Ctrl+Z` 两次。 | 画布首先回退至刚绘制完未移动的状态，然后矩形完全消失。 | 符合预期 |
| **存储和读取** | 1. 绘制包含复杂组合和文本的图形。<br>2. 导出为 `save.json`。<br>3. 清空画布并重新加载。 | 画布重绘，所有图形的形状、尺寸、相对层级、文本及组合树状嵌套关系均复原。 | 符合预期 |

---

## 六、 实验总结与设计展望

### 6.1 设计评估
重构后的系统实现了高内聚、低耦合的架构目标。
*   通过**命令模式**将 UI 操作和核心数据层解耦，有效地避免了在 GUI 控制代码中直接增删图形，使撤销栈逻辑更加清晰。
*   **组合模式**使系统在扩展多重嵌套组合时不需要修改选中及变换机制，表现了开闭原则（OCP）的优良实践。

### 6.2 展望与局限
当前版本仍存在一些提升空间：
1.  **无损缩放限制**：当包含连接线时，等比例缩放仅改变线段起止点，连接线本身的粗细属性尚未支持等比变化。
2.  **文本渲染对齐**：独立文本框在极端纵横比缩放下，其字体边缘裁剪检测逻辑仍有进一步优化的空间。