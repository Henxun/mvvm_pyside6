# 使用 uv 打包并发布到 PyPI 指南

本项目已配置好使用 `uv` 进行打包和发布。以下是详细步骤：

## 前置准备

### 1. 安装 uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 配置 PyPI API Token
在发布到 PyPI 之前，需要获取 API token：
1. 访问 https://pypi.org/manage/account/token/
2. 创建一个新的 API token
3. 复制生成的 token

设置环境变量（推荐方式）：
```bash
export UV_PUBLISH_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxx
```

或者使用配置文件 `~/.config/uv/publish.toml`：
```toml
[pypi]
token = "pypi-xxxxxxxxxxxxxxxxxxxx"
```

## 项目结构

当前项目结构如下：
```
mvvm_framework/
├── pyproject.toml          # 项目配置文件
├── README.md               # 项目说明文档
├── src/
│   └── mvvm_framework/     # 源代码目录
│       ├── __init__.py
│       ├── core/           # 核心模块
│       └── examples/       # 示例代码
└── dist/                   # 构建输出目录
    ├── mvvm_framework-1.0.0.tar.gz
    └── mvvm_framework-1.0.0-py3-none-any.whl
```

## 打包步骤

### 1. 构建分发包
```bash
cd mvvm_framework
uv build
```

这会在 `dist/` 目录下生成两个文件：
- `.tar.gz` 文件：源码分发包
- `.whl` 文件：Wheel 二进制包

### 2. 验证包内容（可选）
```bash
# 查看 wheel 包内容
unzip -l dist/mvvm_framework-1.0.0-py3-none-any.whl

# 或检查 tarball
tar -tzf dist/mvvm_framework-1.0.0.tar.gz
```

## 发布到 PyPI

### 方法一：直接发布（推荐）
```bash
uv publish
```

### 方法二：指定用户名和 token
```bash
uv publish --username __token__ --password pypi-xxxxxxxxxxxxxxxxxxxx
```

### 方法三：使用 TestPyPI 测试
```bash
uv publish --publish-url https://test.pypi.org/legacy/
```

## 发布到 TestPyPI（建议先测试）

1. 获取 TestPyPI token: https://test.pypi.org/manage/account/token/
2. 设置环境变量：
   ```bash
   export UV_PUBLISH_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxx
   ```
3. 发布到 TestPyPI：
   ```bash
   uv publish --publish-url https://test.pypi.org/legacy/
   ```
4. 测试安装：
   ```bash
   pip install --index-url https://test.pypi.org/simple/ mvvm-framework
   ```

## 常见问题

### 1. 包已存在错误
如果版本号已存在，需要：
- 增加 `pyproject.toml` 中的 `version` 号
- 重新构建：`uv build`
- 重新发布：`uv publish`

### 2. 认证失败
确保：
- Token 正确且未过期
- 使用 `__token__` 作为用户名
- 网络连接正常

### 3. 元数据不完整
检查 `pyproject.toml` 是否包含：
- `name`: 包名
- `version`: 版本号
- `description`: 描述
- `readme`: README 文件
- `authors`: 作者信息
- `requires-python`: Python 版本要求
- `dependencies`: 依赖项

## 项目配置说明

当前 `pyproject.toml` 配置：
- 包名：`mvvm-framework`
- 版本：`1.0.0`
- Python 要求：`>=3.12`
- 依赖：`pyside6>=6.0.0`

## 参考资料

- uv 官方文档：https://docs.astral.sh/uv/
- uv 打包指南：https://docs.astral.sh/uv/guides/package/
- PyPI 发布指南：https://pypi.org/help/#file-name
- TestPyPI: https://test.pypi.org/
