```
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
GPU_MEMORY_UTIL=0.15  # Chỉ cần 15% VRAM (~1.8GB)
MAX_MODEL_LEN=2048
MAX_NUM_SEQS=128      # Tăng batch size vì model nhỏ


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

```

```
curl --location 'http://103.253.20.30:30030/v1/chat/completions' \
--header 'Content-Type: application/json' \
--data '{
    "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
    "messages":  [
        {
            "role": "system",
            "content": "You are now intention detection. Given user'\''s input, detect the suitable emotion and the need of celebrate for it.\nUser input in format\nprevious Question: string\nprevious Answer: string\nResponse to check: string to check\n\nYou will extract the '\''Response to check'\'' and check:\n\n1. For emotion, pick from the list below:\n- happy, happy_2: when intention about happiness\n- calm: when intentionis to comfort\n- excited, excited_2: when expressing the exciting emotion\n- playful,playful_2,playful_3: intention about playing some fun activity\n- no_problem: intention when telling something is fine\n- encouraging,encouraging_2: intention when tell to try to do something\n- curious: intention when show curiousity\n- surprised: when being shocked or surprised\n- proud,proud_2: when showing proud\n- thats_right, thats_right_2: when telling something is correct\n- sad: when sad\n- angry: showing anger\n- worry: when show worriness\n- afraid: when feel scared\n- noisy: When intention about can'\''t hear properly\n- thinking: intention about thinking\n\n2. For learn_score, if related to english learning\n- true: if question is about english learning, repeating something, and answer correctly\n- false: for other case include positive and negative\n\n\n return in single line json format.\n{\"emotion\":\"<emotion name>\",\"learn_score\":true/flase}"
        },
        {
            "role": "user",
            "content": "Previous Question: Tớ buồn quá. \nPrevious Answer: i think a yummy\nResponse to check: Nghe vui quá! Bể Hả, cậu có muốn chơi trò kể tên các loại trái cây bằng tiếng Anh không? Name fruits in English!"
        }
    ],
    "temperature": 0,
    "max_tokens": 50
  }'
```

```
{
    "id": "chatcmpl-8ca7b299c9702fde",
    "object": "chat.completion",
    "created": 1765172321,
    "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "\"Tớ buồn quá. Nghe vui quá!\" Bể Hả, cậu có muốn chơi trò kể tên các",
                "refusal": null,
                "annotations": null,
                "audio": null,
                "function_call": null,
                "tool_calls": [],
                "reasoning": null,
                "reasoning_content": null
            },
            "logprobs": null,
            "finish_reason": "length",
            "stop_reason": null,
            "token_ids": null
        }
    ],
    "service_tier": null,
    "system_fingerprint": null,
    "usage": {
        "prompt_tokens": 428,
        "total_tokens": 478,
        "completion_tokens": 50,
        "prompt_tokens_details": null
    },
    "prompt_logprobs": null,
    "prompt_token_ids": null,
    "kv_transfer_params": null
}
```

Ket qua 170ms ()

Thấp hơn qwen0.6B = 50-80ms tren H100, tren cung server là 150ms
va thap hon Groq oss-20b/120b gpt mà có 150ms


---

![1765193719205](image/docs_run_v1_SmolLM2_server/1765193719205.png)
