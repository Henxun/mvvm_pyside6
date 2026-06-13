# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1] - 2026-06-13

### Bug Fixes
- **Binding Handler GC Issue**: Fixed binding handlers being garbage collected due to missing parent parameter. All binding methods (`bind_text`, `bind_checked`, `bind_value`, `bind_command`, `bind_visibility`, `bind_items`, `bind_validation_error`) now pass the widget as parent to ensure handlers remain alive. ([#T1](docs/tasks/fix-binding-gc/T1-fix.md))

## [0.1.0] - Initial Release

### Features
- MVVM framework core components (Model, ViewModel, ObservableObject, ObservableList)
- Data binding utilities (text, checked, value, command, visibility, items, validation)
- Example application demonstrating MVVM pattern with PySide6