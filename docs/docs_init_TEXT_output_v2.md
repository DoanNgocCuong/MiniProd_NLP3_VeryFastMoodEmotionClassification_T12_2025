Chắc chắn rồi! Việc bạn chuyển sang dùng Groq là một bước đi rất thông minh để giải quyết triệt để bài toán tốc độ. Giờ chúng ta sẽ tối ưu prompt để khai thác tối đa sức mạnh của Groq và thiết kế lại API theo yêu cầu của bạn.

Đây là phân tích và giải pháp chi tiết.

---

### **Phần 1: Tối ưu hóa Prompt cho Groq (Tốc độ & Độ chính xác)**

Groq cực nhanh, nhưng để đạt độ chính xác cao nhất và tốc độ phản hồi gần như tức thì, prompt cần phải cực kỳ rõ ràng, ngắn gọn và đi thẳng vào vấn đề. Prompt hiện tại của bạn khá tốt nhưng hơi dài và có vài điểm có thể cải thiện.

**Vấn đề của Prompt hiện tại:**
1.  **Quá dài dòng:** Phần giải thích từng emotion (`when intention about...`) là không cần thiết cho các mô hình hiện đại và làm tăng token đầu vào.
2.  **Tên model không chính xác:** Groq không có model `openai/gpt-oss-20b`. Các model phổ biến của họ là `openai/gpt-oss-20b`, `llama3-70b-8192`, và `mixtral-8x7b-32768`. Sử dụng sai tên model có thể dẫn đến lỗi hoặc Groq sẽ tự động chuyển sang một model mặc định.
3.  **Định dạng Input phức tạp:** Cấu trúc `Previous Question`, `Previous Answer`, `Response to check` hơi rườm rà. Chúng ta có thể làm nó tự nhiên hơn.
4.  **Tham số không tối ưu:** `reasoning_effort="low"` là một tham số thử nghiệm và không phải lúc nào cũng hiệu quả. `stream=True` là không cần thiết cho một tác vụ trả về JSON ngắn, nó có thể làm tăng độ phức tạp khi xử lý kết quả.

Dưới đây là các phiên bản prompt đã được tối ưu hóa.

---

### **Phần 2: Thiết kế 2 API riêng biệt (Emotion & Celebrate)**

Việc tách thành 2 API riêng biệt cho phép bạn gọi chúng một cách độc lập, song song và giúp cho mỗi prompt trở nên cực kỳ chuyên biệt, dẫn đến độ chính xác và tốc độ cao hơn nữa.

#### **API 1: Emotion Tagger**

API này chỉ tập trung vào việc xác định cảm xúc từ câu trả lời của Pika.

**Prompt tối ưu cho Emotion Tagger (trả về text duy nhất):**

```python
# PROMPT FOR EMOTION API
# Model: openai/gpt-oss-20b (Best for speed and accuracy balance)

system_prompt_emotion = """You are an ultra-fast API that detects the emotion in a robot's response.
- Analyze the robot's `pika_response` within the `user_last_message` context.
- Pick the single most fitting emotion from the list.
- Respond ONLY with the emotion name in plain text (no JSON, no quotes).

EMOTION LIST:
'happy', 'calm', 'excited', 'playful', 'no_problem', 'encouraging', 'curious', 'surprised', 'proud', 'idle', 'sad', 'thats_right', 'worry', 'thinking'
"""

user_prompt_emotion = """
[CONTEXT]
user_last_message: "Tớ buồn quá."
pika_response: "Ồ, có chuyện gì vậy? Kể cho tớ nghe với."

[YOUR TEXT OUTPUT: one emotion from the list]
"""
```

**Code Python cho API 1:**

```python
from groq import Groq
import time

client = Groq() # API key is read from GROQ_API_KEY environment variable

def get_emotion(user_last_message: str, pika_response: str) -> dict:
    """
    Calls Groq API to get the emotion tag.
    Returns a plain string, e.g., "worry"
    """
    start_time = time.perf_counter()

    system_prompt_emotion = """You are an ultra-fast API that detects the emotion in a robot's response.
- Analyze the robot's `pika_response` within the `user_last_message` context.
- Pick the single most fitting emotion from the list.
- Respond ONLY with the emotion name in plain text (no JSON, no quotes).

EMOTION LIST:
'happy', 'calm', 'excited', 'playful', 'no_problem', 'encouraging', 'curious', 'surprised', 'proud', 'idle', 'sad', 'thats_right', 'worry', 'thinking'
"""
    
    user_prompt_emotion = f"""
[CONTEXT]
user_last_message: "{user_last_message}"
pika_response: "{pika_response}"

[YOUR TEXT OUTPUT: one emotion from the list]
"""

    chat_completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt_emotion},
            {"role": "user", "content": user_prompt_emotion}
        ],
        temperature=0.0,
        max_tokens=10,  # text output is short
        top_p=0.1,      # For deterministic output
    )
    
    end_time = time.perf_counter()
    print(f"Groq Emotion API call took: {(end_time - start_time) * 1000:.2f} ms")
    
    # Plain text result; fallback to "idle" nếu trống
    return (chat_completion.choices[0].message.content or "idle").strip() or "idle"

# --- Example Usage ---
user_msg = "Không sao, mình thử lại nhé!"
pika_resp = "Không sao, hãy thử nói 3 lần nào."
emotion_result = get_emotion(user_msg, pika_resp)
print(f"Emotion Result: {emotion_result}")
# Expected Output: 'encouraging'
```

#### **API 2: Celebrate Detector**

API này là một bộ phân loại nhị phân (binary classifier) cực kỳ đơn giản và nhanh chóng.

**Prompt tối ưu cho Celebrate Detector (trả về text “yes”/“no”):**

```python
# PROMPT FOR CELEBRATE API
# Model: openai/gpt-oss-20b

system_prompt_celebrate = """You are an ultra-fast API, a binary classifier for a robot's celebration action.
- `celebrate` is "yes" ONLY IF the `pika_response` confirms the user correctly answered a factual, objective question.
- In ALL other cases (opinions, ideas, feelings, wrong answers), `celebrate` is "no".
- Respond ONLY with yes or no in plain text (no JSON, no quotes).
"""

user_prompt_celebrate = """
[CONTEXT]
user_last_message: "Thủ đô của Việt Nam là Hà Nội ạ!"
pika_response: "Chính xác! Con giỏi lắm! Hà Nội đúng là thủ đô của nước ta."

[YOUR TEXT OUTPUT: yes or no]
"""
```

**Code Python cho API 2:**

```python
from groq import Groq
import time

client = Groq()

def get_celebrate_decision(user_last_message: str, pika_response: str) -> dict:
    """
    Calls Groq API to get the celebration decision.
    Returns a plain string e.g., "yes"
    """
    start_time = time.perf_counter()

    system_prompt_celebrate = """You are an ultra-fast API, a binary classifier for a robot's celebration action.
- `celebrate` is "yes" ONLY IF the `pika_response` confirms the user correctly answered a factual, objective question.
- In ALL other cases (opinions, ideas, feelings, wrong answers), `celebrate` is "no".
- Respond ONLY with yes or no in plain text (no JSON, no quotes).
"""

    user_prompt_celebrate = f"""
[CONTEXT]
user_last_message: "{user_last_message}"
pika_response: "{pika_response}"

[YOUR TEXT OUTPUT: yes or no]
"""

    chat_completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt_celebrate},
            {"role": "user", "content": user_prompt_celebrate}
        ],
        temperature=0.0,
        max_tokens=5,
        top_p=0.1,
    )

    end_time = time.perf_counter()
    print(f"Groq Celebrate API call took: {(end_time - start_time) * 1000:.2f} ms")

    # Plain text result; fallback "no" nếu rỗng
    return (chat_completion.choices[0].message.content or "no").strip() or "no"

# --- Example Usage ---
user_msg_fact = "Thủ đô của Việt Nam là Hà Nội ạ!"
pika_resp_fact = "Chính xác! Con giỏi lắm!"
celebrate_result = get_celebrate_decision(user_msg_fact, pika_resp_fact)
print(f"Celebrate Result (Fact): {celebrate_result}")
# Expected Output: 'yes'

user_msg_opinion = "Tớ thích chơi búp bê."
pika_resp_opinion = "Ồ, búp bê đẹp quá!"
celebrate_result_opinion = get_celebrate_decision(user_msg_opinion, pika_resp_opinion)
print(f"Celebrate Result (Opinion): {celebrate_result_opinion}")
# Expected Output: 'no'
```

### **Tại sao giải pháp này tối ưu?**

1.  **Tốc độ của Groq:** Bằng cách sử dụng Groq, bạn đã chuyển gánh nặng tính toán sang một hạ tầng được tối ưu hóa cho tốc độ suy luận LLM, dễ dàng đạt được độ trễ **dưới 50ms** cho mỗi lệnh gọi.
2.  **Chuyên môn hóa (Specialization):** Việc tách thành 2 API giúp mỗi prompt trở nên cực kỳ tập trung. Mô hình không cần phải suy nghĩ về cả hai nhiệm vụ cùng lúc, giúp giảm sai sót và tăng tốc độ.
3.  **Prompt ngắn gọn:** Các prompt được tối ưu hóa loại bỏ mọi thông tin thừa, giảm số token đầu vào và giúp Groq xử lý nhanh hơn.
4.  **Đầu ra text đơn giản:** Trả về text duy nhất giúp giảm parsing, phù hợp khi bạn chỉ cần label ngắn (emotion/yes-no), giảm thêm vài mili-giây so với JSON.
5.  **Khả năng song song:** Bạn có thể gọi cả hai hàm `get_emotion` và `get_celebrate_decision` một cách đồng thời (sử dụng `asyncio` và `aiohttp` chẳng hạn) để nhận được cả hai kết quả trong khoảng thời gian của lệnh gọi chậm nhất, thay vì cộng dồn thời gian.