```bash
vllm serve Qwen/Qwen2.5-0.5B-Instruct-AWQ \
    --host 0.0.0.0 \
    --port 8825 \
    --quantization awq \
    --gpu-memory-utilization 0.5 \
    --enable-prefix-caching \
    --enable-chunked-prefill \
    --max-num-seqs 32 \
    --max-num-batched-tokens 2048 \
    --max-model-len 2048 \
    --dtype half \
    --swap-space 4
```

---

Kiểu 1: 

```
CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.openai.api_server \
  --model 'HuggingFaceTB/SmolLM2-135M-Instruct' \
  --dtype float16 \
  --host 0.0.0.0 \
  --port 30030 \
  --gpu-memory-utilization 0.3 \
  --max-model-len 512 \
  --max-num-seqs 512 \
  --enable-prefix-caching \
  --trust-remote-code \
  --disable-log-requests
```

Kiểu 2:

```
vllm serve Qwen/Qwen2.5-0.5B-Instruct-AWQ \
    --host 0.0.0.0 \
    --port 8825 \
    --quantization awq \
    --gpu-memory-utilization 0.5 \
    --enable-prefix-caching \
    --enable-chunked-prefill \
    --max-num-seqs 32 \
    --max-num-batched-tokens 2048 \
    --max-model-len 2048 \
    --dtype half \
    --swap-space 4
```

Tạo bảng so sánh 2 cái này


Dưới đây là bảng so sánh chi tiết giữa hai cách chạy vLLM server:

| **Thuộc tính** | **Kiểu 1 (Python Module)** | **Kiểu 2 (vLLM CLI)** |
|---|---|---|
| **Lệnh khởi chạy** | `python -m vllm.entrypoints.openai.api_server` | `vllm serve` |
| **CUDA Device** | `CUDA_VISIBLE_DEVICES=0` | Không chỉ định (mặc định) |
| **Model** | HuggingFaceTB/SmolLM2-135M-Instruct | Qwen/Qwen2.5-0.5B-Instruct-AWQ |
| **Model Size** | 135M parameters | 500M parameters |
| **Port** | 30030 | 8825 |
| **Host** | 0.0.0.0 | 0.0.0.0 |
| **Data Type** | float16 | half |
| **GPU Memory Utilization** | 0.3 (30%) | 0.5 (50%) |
| **Max Model Length** | 512 tokens | 2048 tokens |
| **Max Sequences** | 512 | 32 |
| **Max Batched Tokens** | Không chỉ định | 2048 |
| **Quantization** | Không | AWQ |
| **Prefix Caching** | ✅ Enabled | ✅ Enabled |
| **Chunked Prefill** | Không | ✅ Enabled |
| **Swap Space** | Không chỉ định | 4GB |
| **Trust Remote Code** | ✅ Enabled | Không chỉ định |
| **Disable Log Requests** | ✅ Enabled | Không chỉ định |

## **Nhận xét:**

### **Kiểu 1** - Tối ưu cho **throughput cao**:
- Model nhỏ hơn (135M) nhưng hỗ trợ nhiều sequences đồng thời (512)
- Memory utilization thấp (30%)
- Context length ngắn (512 tokens)
- Phù hợp cho các ứng dụng cần xử lý nhiều request ngắn đồng thời

### **Kiểu 2** - Tối ưu cho **quality và context dài**:
- Model lớn hơn (500M) với quantization AWQ để tiết kiệm memory
- Context length dài hơn (2048 tokens)
- Ít sequences đồng thời (32) nhưng mỗi sequence có thể dài hơn
- Có swap space backup và chunked prefill để tối ưu memory
- Phù hợp cho các task cần reasoning phức tạp hoặc context dài