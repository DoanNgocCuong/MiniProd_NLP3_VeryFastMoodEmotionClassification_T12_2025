[8 tools called]

Groq đang được gọi ở `AsyncGroqClient.complete()` và trả về `message.content` (string) rồi `.strip()`, không parse JSON, không schema. Các prompt cũng yêu cầu trả lời thuần văn bản:

```
27:44:src/clients/groq_client_async.py
        content = completion.choices[0].message.content or ""
        return content.strip()
```

```
3:10:src/prompts/emotion_prompt.py
SYSTEM_PROMPT = f"""You are an ultra-fast API that detects the emotion...
- Respond ONLY with the emotion name in plain text (no JSON, no quotes).
```

```
1:5:src/prompts/celebrate_prompt.py
SYSTEM_PROMPT = """You are an ultra-fast API...
- Respond ONLY with yes or no in plain text (no JSON, no quotes).
```

=> Kết luận: Groq trả ra text thuần (một emotion name hoặc “yes”/“no”), không JSON. Dịch vụ `EmotionService`/`CelebrateService` cũng chỉ đọc string đó và map sang enum, không có bước parse JSON nào.