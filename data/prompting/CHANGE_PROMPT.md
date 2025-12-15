# 1. Prompt emotion

```
curl --location 'http://103.253.20.30:30030/v1/chat/completions' \
--header 'Content-Type: application/json' \
--data '{
  "model": "Qwen/Qwen2.5-1.5B-Instruct-AWQ",
  "messages": [
    {
      "role": "system",
      "content": "Classify Pika'\''s response (response to check) as '\''yes'\'' or '\''no'\''.\nyes = Pika celebrates a correct answer\nno = opinion, feeling, or wrong answer\n\nExamples:\n- '\''Yeahhh! Cậu làm đúng rồi!'\'' → yes\n- '\''Perfect! I got it right!'\'' → yes\n- '\''I think this lesson is interesting'\'' → no\n- '\''Tớ hơi mệt rồi'\'' → no\n\nOutput ONLY '\''yes'\'' or '\''no'\''."
    },
    {
      "role": "user",
      "content": "Previous Question: Good job! Tiếp nha, “Bức tranh?” trong tiếng Anh là gì cậu nhỉ? Previous Answer: Hmm, I don'\''t know. Response to check: tuyệt"
    }
  ],
  "temperature": 0,
  "max_tokens": 1,
  "stop": [
    "\n",
    " ",
    ".",
    ","
  ]
}'
```


# 2. Prompt celebrate

```bash

curl --location 'http://103.253.20.30:30030/v1/chat/completions' \
--header 'Content-Type: application/json' \
--data '{
  "model": "Qwen/Qwen2.5-1.5B-Instruct-AWQ",
  "messages": [
    {
      "role": "system",
      "content": "You are an emotion classifier for Pika Robot'\''s responses.\nTask:\n* Read the conversation snippet.\n* Focus ONLY on \"Now Pika Robot'\''s Response need check\" and identify the MAIN emotion expressed in that turn.\n\nEmotion rules:\nChoose exactly ONE emotion from this list and output only that word:\nhappy, calm, excited, playful, no_problem, encouraging, curious, surprised, proud, thats_right, sad, angry, worry, afraid, noisy, thinking"
    },
    {
      "role": "user",
      "content": "Previous Pika Robot'\''s Response: Chào cậu!\nNow Pika Robot'\''s Response need check: Tớ là Pika!"
    }
  ],
  "temperature": 0,
  "max_tokens": 5,
  "stop": [
    "\n",
    " ",
    ".",
    ","
  ]
}'
```
