## 1.1 Prompt ban dau - 150ms 




## 1.2. Prompt tiep theo (van gom chung 1 prompt) - 76-88ms
```
You are now intention detection. Given user's input, detect the suitable emotion and the need of celebrate for it.\nUser input in format\nprevious Question: string\nprevious Answer: string\nResponse to check: string to check\n\nYou will extract the 'Response to check' and check:\n\n1. For emotion, pick from the list below:\n- happy, happy_2: when intention about happiness\n- calm: when intentionis to comfort\n- excited, excited_2: when expressing the exciting emotion\n- playful,playful_2,playful_3: intention about playing some fun activity\n- no_problem: intention when telling something is fine\n- encouraging,encouraging_2: intention when tell to try to do something\n- curious: intention when show curiousity\n- surprised: when being shocked or surprised\n- proud,proud_2: when showing proud\n- thats_right, thats_right_2: when telling something is correct\n- sad: when sad\n- angry: showing anger\n- worry: when show worriness\n- afraid: when feel scared\n- noisy: When intention about can't hear properly\n- thinking: intention about thinking\n\n2. For learn_score, if related to english learning\n- true: if question is about english learning, repeating something, and answer correctly\n- false: for other case include positive and negative\n\n\n return in single line json format.\n{\"emotion\":\"<emotion name>\",\"learn_score\":true/flase}
```

```
Previous Question: Đúng rồi! Cậu giỏi quá!
Previous Answer: Hey guys!
Response to check: Cố thêm một chút nữa thôi
```




```python
from groq import Groq

client = Groq()
completion = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
      {
        "role": "system",
        "content": "You are now intention detection. Given user's input, detect the suitable emotion and the need of celebrate for it.\\nUser input in format\\nprevious Question: string\\nprevious Answer: string\\nResponse to check: string to check\\n\\nYou will extract the 'Response to check' and check:\\n\\n1. For emotion, pick from the list below:\\n- happy, happy_2: when intention about happiness\\n- calm: when intentionis to comfort\\n- excited, excited_2: when expressing the exciting emotion\\n- playful,playful_2,playful_3: intention about playing some fun activity\\n- no_problem: intention when telling something is fine\\n- encouraging,encouraging_2: intention when tell to try to do something\\n- curious: intention when show curiousity\\n- surprised: when being shocked or surprised\\n- proud,proud_2: when showing proud\\n- thats_right, thats_right_2: when telling something is correct\\n- sad: when sad\\n- angry: showing anger\\n- worry: when show worriness\\n- afraid: when feel scared\\n- noisy: When intention about can't hear properly\\n- thinking: intention about thinking\\n\\n2. For learn_score, if related to english learning\\n- true: if question is about english learning, repeating something, and answer correctly\\n- false: for other case include positive and negative\\n\\n\\n return in single line json format.\\n{\\\"emotion\\\":\\\"<emotion name>\\\",\\\"learn_score\\\":true/flase}"
      },
      {
        "role": "user",
        "content": "Previous Question: Đúng rồi! Cậu giỏi quá!\nPrevious Answer: Hey guys!\nResponse to check: Cố thêm một chút nữa thôi"
      },
      {
        "role": "assistant",
        "content": "{\"emotion\":\"encouraging\",\"learn_score\":false}"
      },
      {
        "role": "user",
        "content": ""
      }
    ],
    temperature=0,
    max_completion_tokens=512,
    top_p=1,
    reasoning_effort="low",
    stream=False,
    stop=None
)

print(completion.choices[0].message)
```



## 1.3. Van gom chung 1 prompt nhung format khac di

# 2. Chia nho thanh cac promp 
```
Classify emotion from the conversation. 
Output format: emotion
No JSON. Single word only.

Emotions: happy, calm, excited, playful, no_problem, encouraging, curious, surprised, proud, thats_right, sad, angry, worry, afraid, noisy, thinking
```

```
Previous Question: Đúng rồi! Cậu giỏi quá!
Previous Answer: Hey guys!
Response to check: Cố thêm một chút nữa thôi
```

Repone time: 40-50-60ms 
