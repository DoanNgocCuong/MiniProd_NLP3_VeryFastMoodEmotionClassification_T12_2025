#!/bin/bash
# ============================================================
# RUN PHI-3-MINI EMOTION CLASSIFIER - Sử dụng venv hiện có
# Target: GPU 0 (có ~12GB free VRAM)
# ============================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  RUNNING PHI-3-MINI EMOTION CLASSIFIER     ${NC}"
echo -e "${GREEN}============================================${NC}"

# Configuration
VENV_DIR="$HOME/venv_phi3"
GPU_ID=0
PORT=30030  # Port export ra ngoài để test
MODEL_NAME="microsoft/Phi-3-mini-4k-instruct"
GPU_MEMORY_UTIL=0.45
MAX_MODEL_LEN=2048

# Step 1: Check GPU
echo -e "\n${YELLOW}[1/3] Checking GPU ${GPU_ID} availability...${NC}"
FREE_MEM=$(nvidia-smi -i $GPU_ID --query-gpu=memory.free --format=csv,noheader,nounits)
echo "GPU ${GPU_ID} Free Memory: ${FREE_MEM} MiB"

if [ "$FREE_MEM" -lt 8000 ]; then
    echo -e "${RED}WARNING: GPU ${GPU_ID} has less than 8GB free!${NC}"
    echo "Consider changing GPU_ID in this script."
fi

# Step 2: Check and activate existing venv
echo -e "\n${YELLOW}[2/3] Activating existing Python environment...${NC}"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}ERROR: Virtual environment not found at $VENV_DIR${NC}"
    echo "Please run deploy_phi3_emotion_classification.sh first to create the environment."
    exit 1
fi

source "$VENV_DIR/bin/activate"
echo "✓ Activated venv: $VENV_DIR"

# Verify vLLM is installed
echo "Checking vLLM installation..."
if ! python -c "import vllm" 2>/dev/null; then
    echo -e "${RED}ERROR: vLLM not found in venv!${NC}"
    echo "Please run deploy_phi3_emotion_classification.sh first to install dependencies."
    exit 1
fi

VLLM_VERSION=$(python -c "import vllm; print(vllm.__version__)" 2>/dev/null)
echo "✓ vLLM version: $VLLM_VERSION"

# Verify CUDA
if ! python -c "import torch; assert torch.cuda.is_available()" 2>/dev/null; then
    echo -e "${RED}WARNING: CUDA not available!${NC}"
fi

# Step 3: Launch server
echo -e "\n${YELLOW}[3/3] Launching vLLM server...${NC}"
echo -e "${GREEN}============================================${NC}"
echo "Model: ${MODEL_NAME}"
echo "GPU: ${GPU_ID}"
echo "Port: ${PORT}"
echo "Memory Utilization: ${GPU_MEMORY_UTIL}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Server starting... (model will load if not already cached)"
echo "Press Ctrl+C to stop"
echo ""

# Get script directory for log file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/phi3_server.log"

# Launch
CUDA_VISIBLE_DEVICES=$GPU_ID python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --dtype float16 \
    --host 0.0.0.0 \
    --port $PORT \
    --gpu-memory-utilization $GPU_MEMORY_UTIL \
    --max-model-len $MAX_MODEL_LEN \
    --max-num-seqs 64 \
    --enable-prefix-caching \
    --trust-remote-code \
    2>&1 | tee "$LOG_FILE"
