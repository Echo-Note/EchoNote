FROM postgres:16.9

# 基于 PostgreSQL 16.9 的自定义镜像
# 包含 pgvector 和 Apache AGE 扩展

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive

# 替换为阿里云源以提高下载速度
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-16 \
    libreadline-dev \
    zlib1g-dev \
    flex \
    bison \
    && rm -rf /var/lib/apt/lists/*

# 安装 pgvector 扩展
RUN cd /tmp && \
    git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    cd / && \
    rm -rf /tmp/pgvector

# 安装 Apache AGE 扩展
RUN cd /tmp && \
    git clone --branch PG16/v1.5.0-rc0 https://github.com/apache/age.git && \
    cd age && \
    make && \
    make install && \
    cd / && \
    rm -rf /tmp/age

# 清理构建依赖
RUN apt-get remove -y \
    build-essential \
    git \
    postgresql-server-dev-16 \
    libreadline-dev \
    zlib1g-dev \
    flex \
    bison \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置共享内存大小（用于 HNSW 索引构建）
ENV POSTGRES_SHARED_MEMORY_SIZE=1g

# 复制初始化脚本
COPY init-extensions.sql /docker-entrypoint-initdb.d/00-init-extensions.sql
COPY init-db.sql /docker-entrypoint-initdb.d/01-init-db.sql

# 设置权限
RUN chmod 755 /docker-entrypoint-initdb.d/*.sql

# 暴露端口
EXPOSE 5432

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB || exit 1
