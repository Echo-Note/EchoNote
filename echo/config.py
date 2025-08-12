"""
EchoNote 配置加载模块

本模块负责从 TOML 配置文件、环境变量或默认值加载配置。
配置优先级：TOML > 环境变量 > 默认值
"""

import tomllib  # Python 3.11+
from pathlib import Path
from typing import Any


def load_toml_config(config_path: Path) -> dict[str, Any]:
    """
    从指定路径加载 TOML 配置文件

    Args:
        config_path: TOML 配置文件路径

    Returns:
        Dict[str, Any]: 加载的配置字典，如果无法加载则返回空字典
    """
    if tomllib and config_path.exists():
        try:
            with config_path.open("rb") as f:
                return tomllib.load(f)
        except Exception:  # pragma: no cover
            # 配置解析错误时返回空字典
            return {}
    return {}


def get_config_value(config: dict[str, Any], path: str, default: Any = None) -> Any:
    """
    从配置字典中读取嵌套键，路径用点号分隔，如: "database.url"

    Args:
        config: 配置字典
        path: 点号分隔的配置路径，如 "database.url"
        default: 如果配置不存在时返回的默认值

    Returns:
        Any: 配置值或默认值
    """
    node: Any = config
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node
