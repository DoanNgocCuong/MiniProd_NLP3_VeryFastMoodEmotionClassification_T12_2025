python .\app.py --host 0.0.0.0 --port 30031 --reload 
uvicorn app:app --host 0.0.0.0 --port 30031 --reload
uvicorn src.api.main:app --host 0.0.0.0 --port 30031

nohup python app.py --host 0.0.0.0 --port 30031 --reload > output.log 2>&1 &
nohup python -m http.server 30031 > output_index.log 2>&1 &

Kiểm tra process nào đang sử dụng port 30031:**
```bash
	sudo lsof -i :30031
```
"Super User Do - List Open Files - Internet connections on port 30031" (Dùng quyền admin để liệt kê process nào đang sử dụng port 30031))
**6. Kill process theo PID (nếu có):**
```bash
sudo kill -9 <PID>
```


---


CUDA_VISIBLE_DEVICES=0 nohup python -m vllm.entrypoints.openai.api_server \
    --model 'Qwen/Qwen2.5-1.5B-Instruct-AWQ' \
    --host 0.0.0.0 \
    --port 30030 \
    --quantization awq \
    --dtype half \
    --gpu-memory-utilization 0.3 \
    --max-model-len 512 \
    --max-num-seqs 16 \
    --max-num-batched-tokens 512 \
    --enable-prefix-caching \
    --enable-chunked-prefill \
    --swap-space 4 \
    --trust-remote-code \
    --disable-log-requests > doanngoccuong_qwen2.5-1.5B-Instruct-AWQ_server.log 2>&1 &



