# 验收脚本: Binding Handler GC 问题修复

## Bug 描述
新建一个 Person 后，在右侧表单修改属性，左侧列表没有同步更新。

## 根因
`Binding` 类的 handler（`_TextBindingHandler` 等）没有传递 `parent` 参数，导致被 Python GC 回收，信号连接断开。

## 修复内容
修改了 `src/mvvm_framework/core/binding.py` 中所有绑定方法，传递 `widget` 作为 `parent` 参数。

---

## 验收步骤

### 1. 启动应用
```bash
uv run python -c "import sys; sys.path.insert(0, 'src'); from examples.person_view import main; main()"
```

### 2. 测试场景

#### 场景 A: 新建人物后修改名称
1. 点击 **Add** 按钮，添加新人物
2. 点击左侧列表中的新人物（"New Person"）
3. 在右侧表单的 **Name** 输入框中修改名称（例如输入 "Test Name"）
4. **期望结果**: 左侧列表中对应的人物信息立即更新为 "Person(name=Test Name, age=25)"

#### 场景 B: 新建人物后修改年龄
1. 点击 **Add** 按钮，添加新人物
2. 点击左侧列表中的新人物
3. 在右侧表单的 **Age** 数字框中修改年龄（例如改为 30）
4. **期望结果**: 左侧列表中对应的人物信息立即更新为 "Person(name=New Person, age=30)"

#### 场景 C: 选择已有人物后修改
1. 点击左侧列表中的已有人物（如 "Alice"）
2. 在右侧表单修改名称或年龄
3. **期望结果**: 左侧列表同步更新

### 3. 回归测试（确保其他功能未坏）

| 功能 | 操作 | 期望结果 |
|------|------|----------|
| 添加按钮 | 点击 Add | 左侧列表新增一项 |
| 删除按钮 | 选择人物后点击 Remove | 左侧列表移除该项 |
| Save 按钮 | 修改后点击 Save | 状态显示 "All changes saved" |
| Reset 按钮 | 修改后点击 Reset | 表单恢复原值 |

---

## 验收结论

请运行上述步骤后回复：
- **通过**: 如果所有场景都符合期望结果
- **不通过 + 原因**: 如果有任何场景不符合期望结果