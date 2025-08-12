-- PostgreSQL 扩展初始化脚本
-- 用于自动安装和启用 pgvector 和 Apache AGE 扩展

-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 启用 Apache AGE 扩展
CREATE EXTENSION IF NOT EXISTS age;

-- 加载 AGE 扩展
LOAD 'age';

-- 设置搜索路径以包含 AGE 目录
SET search_path = ag_catalog, "$user", public;

-- 显示已安装的扩展信息
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'age');
