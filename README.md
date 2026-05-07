# PySide6 MVVM Framework

一个基于 PySide6 属性系统实现的通用 QtWidgets MVVM（Model-View-ViewModel）框架。

详细文档请参见 [mvvm_framework/README.md](mvvm_framework/README.md)。

## 快速开始

### 安装依赖

```bash
pip install PySide6
```

### 运行示例

```bash
python -m mvvm_framework.examples.person_view
```

## 核心组件

- **ObservableObject**: 支持属性变更通知的基类
- **Model**: 数据模型层，独立于 UI
- **ViewModel**: 视图模型层，暴露模型数据和命令给视图
- **Command**: 命令模式实现，支持启用/禁用状态
- **Binding**: 数据绑定工具类，简化 View 和 ViewModel 之间的绑定
- **ObservableList**: 可观察列表，支持集合变更通知

## 架构说明

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│    Model    │◄────│  ViewModel   │◄────│    View     │
│  (数据层)    │     │ (视图模型层)  │     │  (视图层)    │
└─────────────┘     └──────────────┘     └─────────────┘
      │                    │                    │
      │                    │                    │
      └────────────────────┴────────────────────┘
                  通过属性系统绑定
```

## 许可证

MIT License
