# PySide6 MVVM Framework

一个基于 PySide6 属性系统实现的通用 QtWidgets MVVM（Model-View-ViewModel）框架。

## 特性

- **ObservableObject**: 支持属性变更通知的基类
- **Model**: 数据模型层，独立于 UI
- **ViewModel**: 视图模型层，暴露模型数据和命令给视图
- **Command**: 命令模式实现，支持启用/禁用状态
- **Binding**: 数据绑定工具类，简化 View 和 ViewModel 之间的绑定
- **ObservableList**: 可观察列表，支持集合变更通知
- **验证系统**: 内置属性验证机制

## 安装依赖

```bash
pip install PySide6
```

## 核心组件

### 1. ObservableObject

所有可观察对象的基类，提供属性变更通知功能：

```python
from mvvm_framework import ObservableObject

class MyObject(ObservableObject):
    def __init__(self):
        super().__init__()
        self._name = ""
        
    @Property(str, notify=nameChanged)
    def name(self):
        return self._name
        
    @name.setter
    def name(self, value):
        if self._name != value:
            self._name = value
            self.nameChanged.emit()
```

### 2. Model

数据模型层，表示业务数据：

```python
from mvvm_framework import Model

class PersonModel(Model):
    def __init__(self):
        super().__init__()
        
    @Property(str)
    def firstName(self):
        return self._get_property_value('firstName', "")
        
    @firstName.setter
    def firstName(self, value):
        self._set_property_value('firstName', value)
```

### 3. ViewModel

视图模型层，连接 Model 和 View：

```python
from mvvm_framework import ViewModel, Command

class PersonViewModel(ViewModel[PersonModel]):
    def __init__(self, model=None):
        super().__init__(model)
        
        # 创建命令
        self.save_command = Command(
            execute=self.save,
            can_execute=self.can_save
        )
        
    def validate(self) -> bool:
        # 验证逻辑
        pass
        
    def save(self):
        # 保存逻辑
        pass
```

### 4. 数据绑定

使用 Binding 工具类简化绑定：

```python
from mvvm_framework import Binding

# 双向绑定属性
Binding.bind_property(
    model, 'firstName',
    text_edit, 'text',
    bidirectional=True
)

# 绑定命令到按钮
Binding.bind_command(button, command)

# 绑定可见性
Binding.bind_visibility(viewModel, 'isLoading', loading_label)
```

## 完整示例

参见 `mvvm_framework.py` 中的 `PersonModel`、`PersonViewModel` 和 `PersonView` 示例。

运行示例（需要 PySide6）：

```bash
python mvvm_framework.py
```

## 架构说明

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│    Model    │◄────│  ViewModel   │◄────│    View     │
│  (数据层)    │     │ (视图模型层)  │     │  (视图层)    │
└─────────────┘     └──────────────┘     └─────────────┘
      │                    │                    │
      │                    │                    │
      └────────────────────┴────────────────────┘
                  通过属性系统绑定
```

## API 参考

### ObservableObject

- `propertyChanged`: 属性变更信号
- `suppress_notifications()`: 上下文管理器，临时抑制通知
- `add_validator(prop_name, validator)`: 添加属性验证器

### ViewModel

- `isLoading`: 是否正在加载
- `isValid`: 当前状态是否有效
- `errorMessage`: 错误消息
- `validate()`: 验证方法
- `register_command(name, command)`: 注册命令

### Command

- `canExecute`: 是否可执行
- `execute()`: 执行命令
- `canExecuteChanged`: 可执行状态变更信号
- `executed`: 执行完成信号

### Binding

- `bind_property()`: 绑定属性
- `bind_command()`: 绑定命令
- `bind_visibility()`: 绑定可见性

## 许可证

MIT License
