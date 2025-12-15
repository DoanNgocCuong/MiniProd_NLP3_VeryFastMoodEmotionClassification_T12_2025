#!/bin/bash
# Example curl command với content có xuống dòng

curl -X POST "http://103.253.20.30:30030/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-1.5B-Instruct-AWQ",
    "messages": [
      {
        "role": "system",
        "content": "Classify Robot'\''s response (response need check) as '\''yes'\'' or '\''no'\''.\nyes = Robot celebrates a correct answer\nno = opinion, feeling, or wrong answer\n\nExamples:\n- '\''Yeahhh! Cậu làm đúng rồi!'\'' → yes\n- '\''Perfect! I got it right!'\'' → yes\n- '\''I think this lesson is interesting'\'' → no\n- '\''Tớ hơi mệt rồi'\'' → no\n\nOutput ONLY '\''yes'\'' or '\''no'\''."
      },
      {
        "role": "user",
        "content": "Previous Robot Pika'\''s Question: So proud of you! Tụi mình học câu tiếp theo nha. Câu này nghĩa là tớ thích táo đó! Cậu thử nói theo tớ, chậm trước nha! I like apples.\n\nPrevious Children '\''s Answer: I like apples.\n\nNow Pika Robot'\''s Response need check: Well done! Giờ nhanh hơn chút nha!"
      }
    ],
    "temperature": 0,
    "max_tokens": 1,
    "stop": ["\n", " ", ".", ","]
  }'


