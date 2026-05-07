# MVVM Framework for PySide6

一个基于 PySide6 属性系统实现的通用 QtWidgets MVVM 框架。

## 项目结构

```text
mvvm_framework/
├── __init__.py              # 包入口，导出核心组件
├── core/                    # 核心模块
│   ├── __init__.py
│   ├── observable.py        # 可观察对象和列表
│   ├── model.py             # 模型基类
│   ├── viewmodel.py         # 视图模型基类
│   ├── command.py           # 命令模式实现
│   └── binding.py           # 数据绑定工具
└── examples/                # 示例代码
    ├── __init__.py
    ├── person_model.py      # Person 模型示例
    ├── person_viewmodel.py  # Person ViewModel 示例
    └── person_view.py       # Person View 示例
```

## 核心组件

### 1. ObservableObject（可观察对象）

所有 MVVM 组件的基类，提供属性变更通知机制。

```python
from mvvm_framework import ObservableObject

class MyObject(ObservableObject):
    def __init__(self):
        super().__init__()
        self._value = 0
    
    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    def value(self, val: int):
        if self._value != val:
            self._value = val
            self.notify_property_changed("value")
```

### 2. Model（模型）

数据模型层，包含业务逻辑和数据验证。

```python
from mvvm_framework import Model

class Person(Model):
    def __init__(self, name: str = "", age: int = 0):
        super().__init__()
        self._name = name
        self._age = age
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        if self._name != value:
            self._name = value
            self.notify_property_changed("name")
    
    def validate_name(self, value: str) -> str | None:
        if not value.strip():
            return "Name cannot be empty"
        return None
```

### 3. ViewModel（视图模型）

连接 Model 和 View 的桥梁，暴露数据和命令给视图。

```python
from mvvm_framework import ViewModel, Command

class PersonViewModel(ViewModel[Person]):
    def __init__(self, model: Person):
        super().__init__(model)
        self._save_command = Command(self.save, self.can_save)
    
    @property
    def name(self) -> str:
        return self.model.name
    
    @name.setter
    def name(self, value: str):
        if self.model.name != value:
            self.model.name = value
            self.notify_property_changed("name")
    
    @property
    def save_command(self) -> Command:
        return self._save_command
    
    def can_save(self) -> bool:
        return self.model.name != ""
    
    def save(self):
        print(f"Saving {self.model.name}")
```

### 4. Command（命令）

实现命令模式，用于处理用户操作。

```python
from mvvm_framework import Command

# 基本命令
save_cmd = Command(
    execute=lambda: print("Saved!"),
    can_execute=lambda: True
)

# 带参数的命令
from mvvm_framework.core.command import ParameterizedCommand
delete_cmd = ParameterizedCommand(
    execute=lambda item: print(f"Deleting {item}"),
    can_execute=lambda item: item is not None
)
```

### 5. ObservableList（可观察列表）

支持变更通知的列表类型。

```python
from mvvm_framework import ObservableList

numbers = ObservableList([1, 2, 3])
numbers.itemAdded.connect(lambda idx, val: print(f"Added {val} at {idx}"))
numbers.append(4)  # 触发 itemAdded 信号
```

### 6. Binding（数据绑定）

简化 View 和 ViewModel 之间的绑定。

```python
from mvvm_framework import Binding

# 双向文本绑定
Binding.bind_text(viewmodel, "name", line_edit)

# 单向标签绑定
Binding.bind_label(viewmodel, "display_name", label)

# 命令绑定
Binding.bind_command(viewmodel, "save_command", button)

# 值绑定（SpinBox/Slider）
Binding.bind_value(viewmodel, "age", spinbox)

# 选中状态绑定
Binding.bind_checked(viewmodel, "is_active", checkbox)
```

## 完整示例

运行示例应用：

```bash
python -m mvvm_framework.examples.person_view
```

或者在代码中使用：

```python
import sys
from PySide6.QtWidgets import QApplication
from mvvm_framework.examples import Person, PersonViewModel, PersonView

app = QApplication(sys.argv)

# 创建 Model
person = Person(name="John", age=30, email="john@example.com")

# 创建 ViewModel
viewmodel = PersonViewModel(person)

# 创建 View
view = PersonView(viewmodel)
view.show()

sys.exit(app.exec())
```

## 特性

- **属性变更通知**: 自动通知 UI 更新
- **双向数据绑定**: View 和 ViewModel 自动同步
- **命令模式**: 统一的动作处理方式
- **数据验证**: 内置验证系统
- **计算属性缓存**: 优化性能
- **集合变更通知**: ObservableList 支持
- **类型提示**: 完整的类型注解支持

## 安装依赖

```bash
pip install PySide6
```

## 许可证

MIT License
