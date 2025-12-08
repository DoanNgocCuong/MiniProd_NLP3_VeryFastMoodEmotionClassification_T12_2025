CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.openai.api_server \
    --model "microsoft/Phi-3-mini-4k-instruct" \
    --quantization awq \
    --port 7863 \
    --gpu-memory-utilization 0.85