```
#!/bin/bash
# ============================================================
# DEPLOY PHI-3-MINI EMOTION CLASSIFIER - RTX 3090 Server
# Target: GPU 0 (có ~12GB free VRAM)
# ============================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  DEPLOYING PHI-3-MINI EMOTION CLASSIFIER  ${NC}"
echo -e "${GREEN}============================================${NC}"

# Configuration
VENV_DIR="$HOME/venv_phi3"
GPU_ID=0
PORT=30030  # Port export ra ngoài để test
MODEL_NAME="microsoft/Phi-3-mini-4k-instruct"
GPU_MEMORY_UTIL=0.45
MAX_MODEL_LEN=2048
PYTHON_BIN="/usr/bin/python3.11"  # vLLM requires Python >= 3.9

# Step 1: Check GPU
echo -e "\n${YELLOW}[1/5] Checking GPU ${GPU_ID} availability...${NC}"
FREE_MEM=$(nvidia-smi -i $GPU_ID --query-gpu=memory.free --format=csv,noheader,nounits)
echo "GPU ${GPU_ID} Free Memory: ${FREE_MEM} MiB"

if [ "$FREE_MEM" -lt 30031 ]; then
    echo -e "${RED}WARNING: GPU ${GPU_ID} has less than 8GB free!${NC}"
    echo "Consider changing GPU_ID in this script."
fi

# Step 2: Clean old venv and create new
echo -e "\n${YELLOW}[2/5] Setting up Python environment...${NC}"

# Verify Python 3.11 exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo -e "${RED}ERROR: Python 3.11 not found at $PYTHON_BIN${NC}"
    echo "vLLM requires Python >= 3.9"
    exit 1
fi

echo "Using Python: $($PYTHON_BIN --version)"

if [ -d "$VENV_DIR" ]; then
    echo "Removing old venv..."
    rm -rf "$VENV_DIR"
fi

$PYTHON_BIN -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
echo "Created venv: $VENV_DIR"

# Step 3: Upgrade pip and install dependencies
echo -e "\n${YELLOW}[3/5] Installing dependencies (may take 2-3 minutes)...${NC}"

# Move to home directory to avoid any local pyproject.toml issues
cd "$HOME"

# Upgrade pip first
pip install --upgrade pip wheel setuptools -q

# Clear pip cache to avoid corrupted packages
pip cache purge 2>/dev/null || true

echo "Installing vLLM (this may take a few minutes)..."
# Install vLLM with explicit version - quotes are important!
pip install "vllm>=0.6.0" -q 2>&1 || {
    echo -e "${RED}First attempt failed, trying alternative...${NC}"
    pip install vllm -q
}

echo "Installing requests..."
pip install requests -q

echo -e "${GREEN}Dependencies installed successfully!${NC}"

# Return to original directory
cd -

# Step 4: Verify installation
echo -e "\n${YELLOW}[4/5] Verifying installation...${NC}"
python -c "import vllm; print(f'vLLM version: {vllm.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Step 5: Launch server
echo -e "\n${YELLOW}[5/5] Launching vLLM server...${NC}"
echo -e "${GREEN}============================================${NC}"
echo "Model: ${MODEL_NAME}"
echo "GPU: ${GPU_ID}"
echo "Port: ${PORT}"
echo "Memory Utilization: ${GPU_MEMORY_UTIL}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Server starting... (first run will download model ~2.5GB)"
echo "Press Ctrl+C to stop"
echo ""

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
    2>&1 | tee phi3_server.log
```


----
```bash
curl --location 'http://103.253.20.30:30030/v1/chat/completions' \
--header 'Content-Type: application/json' \
--data '{
    "model": "microsoft/Phi-3-mini-4k-instruct",
    "messages": [
      {
        "role": "system",
        "content": "You are a Mood & Celebrate Tagger. Output JSON only.\n\nRules:\n- celebrate=\"yes\" ONLY if confirming a FACTUAL answer is correct\n- celebrate=\"no\" for opinions, ideas, wrong answers\n\nTags: happy, excited, proud, encouraging, curious, surprised, calm, playful, thats_right, sad, worry, thinking\n\nFormat: {\"emotion_name\": \"<tag>\", \"celebrate\": \"yes\"|\"no\"}"
      },
      {
        "role": "user", 
        "content": "user_last_message: \"Thủ đô của Việt Nam là Hà Nội ạ!\"\npika_response: \"Chính xác! Con giỏi lắm! Hà Nội đúng là thủ đô của nước ta.\"\nOutput:"
      }
    ],
    "temperature": 0,
    "max_tokens": 50
  }'
```

```bash
{
    "id": "chatcmpl-9ef134a40641a940",
    "object": "chat.completion",
    "created": 1765169303,
    "model": "microsoft/Phi-3-mini-4k-instruct",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": " {\"emotion_name\": \"proud\", \"celebrate\": \"yes\"}",
                "refusal": null,
                "annotations": null,
                "audio": null,
                "function_call": null,
                "tool_calls": [],
                "reasoning": null,
                "reasoning_content": null
            },
            "logprobs": null,
            "finish_reason": "stop",
            "stop_reason": 32007,
            "token_ids": null
        }
    ],
    "service_tier": null,
    "system_fingerprint": null,
    "usage": {
        "prompt_tokens": 196,
        "total_tokens": 216,
        "completion_tokens": 20,
        "prompt_tokens_details": null
    },
    "prompt_logprobs": null,
    "prompt_token_ids": null,
    "kv_transfer_params": null
}
```

response time = 300ms