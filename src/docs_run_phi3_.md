```bash
curl --location 'http://103.253.20.30:30030/v1/chat/completions' \
--header 'Content-Type: application/json' \
--data '{
    "model": "microsoft/Phi-3-mini-4k-instruct",
    "messages": [
      {
        "role": "system",
        "content": "You are a Mood & Celebrate Tagger. Output JSON only.\n\nRules:\n- celebrate=\"yes\" ONLY if confirming a FACTUAL answer is correct\n- celebrate=\"no\" for opinions, ideas, wrong answers\n\nTags: happy, excited, proud, encouraging, curious, surprised, calm, playful, thats_right, sad, worry, thinking\n\nFormat: {\"emotion_name\": \"<tag>\", \"celebrate\": \"yes\"|\"no\"}"
      },
      {
        "role": "user", 
        "content": "user_last_message: \"Thủ đô của Việt Nam là Hà Nội ạ!\"\npika_response: \"Chính xác! Con giỏi lắm! Hà Nội đúng là thủ đô của nước ta.\"\nOutput:"
      }
    ],
    "temperature": 0,
    "max_tokens": 50
  }'
```

---
```bash
{
    "id": "chatcmpl-9ef134a40641a940",
    "object": "chat.completion",
    "created": 1765169303,
    "model": "microsoft/Phi-3-mini-4k-instruct",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": " {\"emotion_name\": \"proud\", \"celebrate\": \"yes\"}",
                "refusal": null,
                "annotations": null,
                "audio": null,
                "function_call": null,
                "tool_calls": [],
                "reasoning": null,
                "reasoning_content": null
            },
            "logprobs": null,
            "finish_reason": "stop",
            "stop_reason": 32007,
            "token_ids": null
        }
    ],
    "service_tier": null,
    "system_fingerprint": null,
    "usage": {
        "prompt_tokens": 196,
        "total_tokens": 216,
        "completion_tokens": 20,
        "prompt_tokens_details": null
    },
    "prompt_logprobs": null,
    "prompt_token_ids": null,
    "kv_transfer_params": null
}
```