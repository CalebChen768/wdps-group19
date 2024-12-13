# 使用基础镜像
FROM karmaresearch/wdps2

# 设置工作目录
WORKDIR /home/user

# 复制依赖文件
COPY requirements.txt /home/user/requirements.txt

# 禁用缓存并安装依赖
RUN pip install --no-cache-dir --prefer-binary -r /home/user/requirements.txt && \
    python3 -m spacy download en_core_web_sm && \
    python3 -m spacy download en_core_web_md

# 保持容器运行状态
CMD ["tail", "-f", "/dev/null"]
