# 1. 使用官方预编译好、带有全套环境的轻量级 Python 镜像
FROM python:3.10-slim

# 2. 设置容器内部的工作目录
WORKDIR /app

# 3. 把当前仓库的所有文件复制到容器里的 /app 目录
COPY . /app

# 4. 使用 --no-cache-dir 极速安装依赖，防止免费服务器内存炸掉
RUN pip install --no-cache-dir -r requirements.txt

# 5. 声明容器内部监听的端口
EXPOSE 10000

# 6. 最终启动命令（Render 会自动分发 $PORT 端口）
# 删掉 main.py 后面的 .py，精准对齐 uvicorn 的标准语法
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
