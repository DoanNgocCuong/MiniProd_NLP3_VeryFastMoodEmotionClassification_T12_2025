# A Trúc chỉ 1 cách chạy rất đơn giản những cũng ko xử lý được 
```
vllm serve --model HuggingFaceTB/SmolLM2-135M-Instruct  --host 0.0.0.0  --port 30030  --gpu-memory-utilization 0.3  --max-model-len 2048 
```

Vẫn bị lâu: 150-170ms (trong khi hôm qua deploy con Qwen3_0.6B thì chỉ 100-120ms)

---

