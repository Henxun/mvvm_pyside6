# TASK: T1-fix - Binding Handler GC 问题修复

## Status: Done

## Bug 描述
新建一个 Person 后，在右侧表单修改属性，左侧列表没有同步更新。

## 根因
`Binding` 类的 handler（`_TextBindingHandler` 等）没有传递 `parent` 参数，导致被 Python GC 回收，信号连接断开。

## 修复内容
修改了 `src/mvvm_framework/core/binding.py` 中所有绑定方法，传递 `widget` 作为 `parent` 参数：
- `bind_text`: `_TextBindingHandler(..., parent=widget)`
- `bind_checked`: `_CheckedBindingHandler(..., parent=widget)`
- `bind_value`: `_ValueBindingHandler(..., parent=widget)`
- `bind_command`: `_CommandBindingHandler(..., parent=widget)`
- `bind_visibility`: `_VisibilityBindingHandler(..., parent=widget)`
- `bind_items`: `_ItemsBindingHandler(..., parent=widget)`
- `bind_validation_error`: `_ValidationBindingHandler(..., parent=widget)`

## TDD 微步清单
- M1: reproducing test → RED "handler 被 GC 回收后信号连接断开"
- M2: 修复 binding.py → GREEN
- M3: 验证修复效果 → GREEN

## 验收结果
用户在真实平台验证通过。