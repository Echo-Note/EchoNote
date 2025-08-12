# EchoNote — 基于 Django 的个人博客系统

## 简介

EchoNote 是一个使用 Django 构建的轻量级个人博客站点，支持文章发布、标签、Markdown 渲染与静态资源管理，适合个人学习与部署使用。

## 特性

- 基于 Django 5 构建，Python 3.12+
- 支持 Markdown（代码高亮可自行扩展）
- 文章标签（django-taggit）
- 图片上传（Pillow）
- 12-factor 配置（django-environ）
- 静态文件服务（Whitenoise，生产可用）
- 完整的开发工具链（Ruff/Black/isort/pytest/coverage/mypy）

## 项目结构

```
.
├── echo/                     # 站点/应用源码（示例包名，实际以你的项目为准）
├── manage.py
├── pyproject.toml            # 依赖与工具配置
├── README.md
└── db.sqlite3                # 默认开发数据库
```

## 环境与依赖

- Python 3.12+
- 使用 uv 管理依赖与虚拟环境（推荐）。项目采用 PEP 621/pyproject.toml 进行依赖管理。

## 安装

1) 创建并激活虚拟环境

```shell
uv venv .venv
source .venv/bin/activate
```

2) 安装开发依赖（含 PostgreSQL 驱动）

```shell
uv pip install -e .[dev,postgres]
```

3) 生产部署依赖（可选）

```shell
uv pip install -e .[prod,postgres]
```

4) 安装 git pre-commit 钩子（可选，但推荐）

```shell
uv pip install pre-commit
pre-commit install
```

## 快速开始

1) 初始化数据库

```shell
   uv run python manage.py migrate
```

2) 创建超级用户（可选）

```shell
   uv run python manage.py createsuperuser
```

3) 运行开发服务器

```shell
   uv run python manage.py runserver
```

## 环境变量与配置

项目使用 django-environ 支持从 .env 加载配置。你可以在项目根目录创建 .env 文件，例如：

```dotenv
   DEBUG=true
   SECRET_KEY=change-me
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=postgres://user:pass@localhost:5432/echonote
   # 可选：开发用 SQLite 示例
   # DATABASE_URL=sqlite:///db.sqlite3
```

## 静态与媒体文件

- 开发环境使用 Django 默认静态文件设置
- 生产建议启用 Whitenoise 并在 settings.py 中正确配置 STATIC_ROOT/STATIC_URL
- 如有图片/附件上传，请配置 MEDIA_ROOT/MEDIA_URL 并设置相应的反向代理/存储

## 测试与质量

- 运行测试：

```shell
uv run pytest -q
```

- 覆盖率：

```shell
uv run coverage run -m pytest && uv run coverage report
```

- 代码格式 & 质量：

```shell
uv run ruff check .
uv run ruff format .
uv run black .
uv run isort .
```

- 使用 git pre-commit 钩子自动检查代码质量（安装后会在每次 git commit 时自动运行）

## 类型检查（可选）

项目已配置 mypy 与 django-stubs，启用前请确保 settings 模块路径正确（默认 echonote.settings）：

```shell
uv run mypy .
```

## 部署建议

- 使用 gunicorn + Whitenoise 简化部署：

```shell
uv pip install -e .[prod,postgres]
uv run python manage.py collectstatic --noinput
uv run gunicorn echonote.wsgi:application --bind 0.0.0.0:8000
```

- 请在环境变量中配置 SECRET_KEY、ALLOWED_HOSTS、DATABASE_URL、DEBUG=false 等
- 如部署到 PaaS/容器平台，确保静态文件已 collectstatic，媒体文件有持久化存储

## 常见问题

1) 收不到静态文件？请确认 DEBUG、STATIC_URL、STATIC_ROOT、Whitenoise 中间件是否按顺序配置，并执行过 collectstatic。
2) 数据库连接失败？检查 DATABASE_URL 格式以及对应驱动是否安装（postgres/mysql）。
3) ImportError: echonote.settings 未找到？请检查你的 Django 项目包名与 DJANGO_SETTINGS_MODULE 是否一致。

## 许可证

MIT

## 致谢

如果本项目对你有帮助，欢迎 Star 或提出 Issue/PR。
