#!/bin/bash
# ============================================================
# RUN SMOLLM2-135M EMOTION CLASSIFIER - Ultra Fast Tiny Model
# Target: GPU 0 (~12GB free VRAM - nhưng model này chỉ cần ~300MB!)
# Dự kiến latency: < 10ms (nhanh hơn Phi-3 gấp 3-5 lần)
# ============================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  SMOLLM2-135M EMOTION CLASSIFIER (ULTRA)   ${NC}"
echo -e "${GREEN}============================================${NC}"

# Configuration
VENV_DIR="$HOME/venv_phi3"  # Tái sử dụng venv cũ
GPU_ID=0
PORT=30030
MODEL_NAME="HuggingFaceTB/SmolLM2-135M-Instruct"  # ⚡ TINY MODEL
GPU_MEMORY_UTIL=0.3  # Chỉ cần 15% VRAM (~1.8GB)
MAX_MODEL_LEN=512
MAX_NUM_SEQS=512      # Tăng batch size vì model nhỏ


# Step 1: Check GPU
echo -e "\n${YELLOW}[1/3] Checking GPU ${GPU_ID} availability...${NC}"
FREE_MEM=$(nvidia-smi -i $GPU_ID --query-gpu=memory.free --format=csv,noheader,nounits)
echo "GPU ${GPU_ID} Free Memory: ${FREE_MEM} MiB"

if [ "$FREE_MEM" -lt 2000 ]; then
    echo -e "${RED}WARNING: GPU ${GPU_ID} has less than 2GB free!${NC}"
    echo "SmolLM2-135M only needs ~300MB, but 2GB is recommended for overhead."
fi


# Step 2: Activate venv
echo -e "\n${YELLOW}[2/3] Activating Python environment...${NC}"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}ERROR: Virtual environment not found at $VENV_DIR${NC}"
    echo "Creating new venv..."
    python3.11 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    
    echo "Installing vLLM..."
    pip install --upgrade pip
    pip install vllm==0.12.0 torch==2.5.1
else
    source "$VENV_DIR/bin/activate"
    echo "✓ Activated venv: $VENV_DIR"
fi

# Verify
if ! python -c "import vllm" 2>/dev/null; then
    echo -e "${RED}ERROR: vLLM not found!${NC}"
    exit 1
fi

VLLM_VERSION=$(python -c "import vllm; print(vllm.__version__)" 2>/dev/null)
echo "✓ vLLM version: $VLLM_VERSION"


# Step 3: Launch server
echo -e "\n${YELLOW}[3/3] Launching vLLM server...${NC}"
echo -e "${GREEN}============================================${NC}"
echo "Model: ${MODEL_NAME} (135M params)"
echo "GPU: ${GPU_ID}"
echo "Port: ${PORT}"
echo "Memory Utilization: ${GPU_MEMORY_UTIL} (~300MB only)"
echo "Expected Latency: < 10ms per request"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "🚀 ULTRA-FAST MODE: SmolLM2 is 3.7x smaller than Qwen-0.5B"
echo "Server starting... Press Ctrl+C to stop"
echo ""

# Log file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/smollm2_server.log"

# Launch vLLM với SmolLM2-135M
# NOTE: Model này không có sẵn AWQ version, nhưng FP16 đã đủ nhanh!
CUDA_VISIBLE_DEVICES=$GPU_ID python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --dtype float16 \
    --host 0.0.0.0 \
    --port $PORT \
    --gpu-memory-utilization $GPU_MEMORY_UTIL \
    --max-model-len $MAX_MODEL_LEN \
    --max-num-seqs $MAX_NUM_SEQS \
    --enable-prefix-caching \
    --trust-remote-code \
    --disable-log-requests \
    2>&1 | tee "$LOG_FILE"


# ALTERNATIVE: Nếu muốn quantize thủ công để nhanh hơn nữa
# Uncomment dòng dưới và comment block trên
# CUDA_VISIBLE_DEVICES=$GPU_ID python -m vllm.entrypoints.openai.api_server \
#     --model "prithivMLmods/SmolLM2-135M-GGUF" \
#     --quantization gguf \
#     --dtype auto \
#     --host 0.0.0.0 \
#     --port $PORT \
#     --gpu-memory-utilization $GPU_MEMORY_UTIL \
#     --max-model-len $MAX_MODEL_LEN \
#     --max-num-seqs $MAX_NUM_SEQS \
#     --enable-prefix-caching \
#     --trust-remote-code \
#     2>&1 | tee "$LOG_FILE"
