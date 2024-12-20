#!/bin/bash

# 检查输入参数
if [ $# -eq 0 ]; then
  PARALLEL_INSTANCES=1  # 默认并行实例数量
else
  # 解析 --parall 参数
  for ARG in "$@"; do
    case $ARG in
      --parall=*)
        PARALLEL_INSTANCES="${ARG#*=}"
        shift
        ;;
      *)
        echo "Unknown argument: $ARG"
        exit 1
        ;;
    esac
  done
fi

# 限制实例数量为 1 到 4
if [ "$PARALLEL_INSTANCES" -lt 1 ] || [ "$PARALLEL_INSTANCES" -gt 4 ]; then
  echo "Error: parallel_instances must be between 1 and 4."
  exit 1
fi

# 初始化缓存卷
echo "Initializing cache volume..."
docker volume create wdps-group19_wdps-cache
REAL_PATH=$(docker volume inspect wdps-group19_wdps-cache | grep '"Mountpoint"' | sed -E 's/.*"Mountpoint": "(.*)",/\1/')
if [ -z "$REAL_PATH" ]; then
  echo "Error: Could not find mountpoint for volume wdps-group19_wdps-cache."
  exit 1
fi
sudo mkdir -p "$REAL_PATH/pip"
sudo chmod -R 777 "$REAL_PATH"

# 清理旧容器
echo "Stopping and removing existing wdps-instance containers..."
docker ps -a --filter "name=wdps-instance" --format "{{.ID}}" | xargs -r docker stop
docker ps -a --filter "name=wdps-instance" --format "{{.ID}}" | xargs -r docker rm

# 构建镜像（首次运行需要）
echo "Building Docker image..."
docker-compose build

# 启动指定数量的容器
echo "Starting $PARALLEL_INSTANCES container(s) with Docker Compose..."
docker-compose up -d --scale wdps-instance=$PARALLEL_INSTANCES

# 检查容器是否成功启动
RUNNING_CONTAINERS=$(docker ps --filter "name=wdps-instance" --format "{{.Names}}" | wc -l)
if [ "$RUNNING_CONTAINERS" -ne "$PARALLEL_INSTANCES" ]; then
  echo "Error: Expected $PARALLEL_INSTANCES containers, but only $RUNNING_CONTAINERS are running."
  exit 1
fi

echo "All $PARALLEL_INSTANCES container(s) are ready!"
