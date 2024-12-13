#!/bin/sh

# 设置根目录和输入输出目录
ROOT_DIR=$(dirname "$(realpath "$0")")
INPUT_OUTPUT_DIR="$ROOT_DIR/input_and_output"

# 默认参数
INPUT_FILE="$INPUT_OUTPUT_DIR/example_input.txt"
FINAL_OUTPUT="$INPUT_OUTPUT_DIR/final_output.txt"
PROMPT_MODE="False"
PARALLEL_INSTANCES=1

# 解析参数
while [ $# -gt 0 ]; do
  case $1 in
    --path=*)
      INPUT_FILE="${1#*=}"
      shift
      ;;
    --output=*)
      FINAL_OUTPUT="${1#*=}"
      shift
      ;;
    --prompt)
      PROMPT_MODE="True"
      shift
      ;;
    --parall=*)
      PARALLEL_INSTANCES="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# 检查输入文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: Input file not found: $INPUT_FILE"
  exit 1
fi

# 限制实例数量为 1 到 4
if [ "$PARALLEL_INSTANCES" -lt 1 ] || [ "$PARALLEL_INSTANCES" -gt 4 ]; then
  echo "Error: parallel_instances must be between 1 and 4."
  exit 1
fi

# 确保输出目录存在
mkdir -p "$INPUT_OUTPUT_DIR"

# Step 1: 分割输入文件
# 排除空行，确保行数计算正确
TOTAL_LINES=$(grep -cve '^\s*$' "$INPUT_FILE")
LINES_PER_PART=$(( (TOTAL_LINES + PARALLEL_INSTANCES - 1) / PARALLEL_INSTANCES ))

echo "Splitting input file into $PARALLEL_INSTANCES parts..."

START_LINE=1
for i in $(seq 1 "$PARALLEL_INSTANCES"); do
  END_LINE=$(( START_LINE + LINES_PER_PART - 1 ))
  if [ "$END_LINE" -gt "$TOTAL_LINES" ]; then
    END_LINE=$TOTAL_LINES
  fi
  sed -n "${START_LINE},${END_LINE}p" "$INPUT_FILE" > "$INPUT_OUTPUT_DIR/input_instance_${i}.txt"
  START_LINE=$(( END_LINE + 1 ))
done

# Step 2: 清理旧容器并启动新容器
echo "Stopping and removing existing wdps-instance containers..."
docker ps -a --filter "name=wdps-instance" --format "{{.ID}}" | xargs -r docker stop
docker ps -a --filter "name=wdps-instance" --format "{{.ID}}" | xargs -r docker rm

echo "Starting $PARALLEL_INSTANCES container(s) with Docker Compose..."
docker-compose up -d --scale wdps-instance=$PARALLEL_INSTANCES

# 检查容器数量是否正确
RUNNING_CONTAINERS=$(docker ps --filter "name=wdps-instance" --format "{{.Names}}" | wc -l)
if [ "$RUNNING_CONTAINERS" -ne "$PARALLEL_INSTANCES" ]; then
  echo "Error: Expected $PARALLEL_INSTANCES containers, but only $RUNNING_CONTAINERS are running."
  exit 1
fi

# Step 3: 分配任务
for INDEX in $(seq 1 "$PARALLEL_INSTANCES"); do
  CONTAINER_NAME="wdps-group19-wdps-instance-$INDEX"
  INPUT_PART="$INPUT_OUTPUT_DIR/input_instance_${INDEX}.txt"
  OUTPUT_PART="$INPUT_OUTPUT_DIR/output_instance_${INDEX}.txt"
  echo "Running container $CONTAINER_NAME with input $INPUT_PART and output $OUTPUT_PART..."
  docker exec "$CONTAINER_NAME" python3 /home/user/code/run_task1.py \
    --path="/home/user/input_and_output/$(basename "$INPUT_PART")" \
    --output="/home/user/input_and_output/$(basename "$OUTPUT_PART")" \
    --prompt="$PROMPT_MODE" &
done

# Step 4: 等待所有任务完成
wait
echo "All containers have finished processing."

# Step 5: 合并输出文件
echo "Merging output files into $FINAL_OUTPUT..."
cat "$INPUT_OUTPUT_DIR"/output_instance_*.txt > "$FINAL_OUTPUT"

# Step 6: 删除临时文件
echo "Cleaning up temporary files..."
rm -f "$INPUT_OUTPUT_DIR"/input_instance_*.txt
rm -f "$INPUT_OUTPUT_DIR"/output_instance_*.txt

echo "Task completed. Final output saved to $FINAL_OUTPUT."
