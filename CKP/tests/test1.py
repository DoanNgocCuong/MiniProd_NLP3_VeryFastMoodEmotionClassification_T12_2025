import time
from groq import Groq  # <- FIX: Import Groq

client = Groq(api_key="")

start_time = time.time()
completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
      {
        "role": "system",
        "content": "· 'celebrate' is \"yes\" ONLY IF the 'pika_response' confirms the user correctly\n  answered a factual, objective question.\n· In ALL other cases (opinions, ideas, feelings, wrong answers), 'celebrate' is\n  \"no\".\n· Respond ONLY text: yes/no\n"
      },
      {
        "role": "user",
        "content": "Previous Question: Yay, you did it! Giờ nhanh hơn một chút nha! Picture \nPrevious Answer: Picture \nResponse to check: Great job! Giờ thì như người bản ngữ luôn nhé!"
      }
    ],
    temperature=0,
    max_completion_tokens=512,
    top_p=1,
    stream=False,
    stop=None
)

end_time = time.time()
response_time = end_time - start_time

print(completion.choices[0].message)
print(f"Response time: {response_time:.2f} seconds")


# Response time: 0.53 seconds