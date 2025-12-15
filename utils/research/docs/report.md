![1765194039477](image/report/1765194039477.png)

![1765194063739](image/report/1765194063739.png)


Hôm nay em có test 1 số model nhỏ : `HuggingFaceTB/SmolLM2-135M-Instruct<span></span>`, `HuggingFaceTB/SmolLM2-360M-Instruct<span></span>`, Qwen3-0.6B (con của a Trúc hôm qua ạ), **H2O-Danube3-500M-Chat**
**---**
Response time đều quay quay 150ms (trong ảnh là con 135M response time là 170ms, em tìm cách tối ưu response time nhưng chưa tối ưu được ạ, em có nhờ a Trúc qua xem cách deploy - a Trúc deploy lại nhưng kết quả vẫn không đổi)

=> Em quay lại test Groq(gpt-oss-20b) : hôm qua là 150ms
Hôm nay em :
+, Tối ưu Prompt (viết ngắn hơn) => response time vào khoảng 100ms. Chẻ thành 2 Prompt 1 cái cho celbrate, 1 cái cho emotion => response time còn khoảng 60-80ms
+, Chỉnh các tham số khác max_token output, ...
**
---**

**Hiện nay em thấy khi host model lên thì performance tốt nhất khi chạy 1 request cũng rơi vào 120ms + độ ổn định khi chạy số lượng lớn không cao + tài nguyên máy
Dùng Groq 1 request rơi vào khoảng 50-80ms + Đã chạy Product cho nhiều bài trước đây + ổn định + ...**
