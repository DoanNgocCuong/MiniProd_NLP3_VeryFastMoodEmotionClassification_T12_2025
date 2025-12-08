#!/usr/bin/env python3
"""
Test Emotion Classifier - Phi-3-mini on vLLM
Benchmark latency và accuracy cho bài toán phân loại emotion/celebrate
"""

import requests
import json
import time
import statistics
from typing import Dict, List, Tuple

# ============================================================
# CONFIGURATION
# ============================================================
API_URL = "http://localhost:7863/v1/chat/completions"  # Port của Phi-3-mini server
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"

# System prompt tối ưu
SYSTEM_PROMPT = """You are a high-speed Mood & Celebrate Tagger for a child-robot interaction system.

# TASK
Analyze the robot's response and output JSON with 2 fields: emotion_name and celebrate.

# INSTRUCTIONS
1. Analyze user_last_message: Is user answering a factual question or just chatting?
2. Analyze pika_response for emotion
3. celebrate Logic:
   - "yes" ONLY IF Pika confirms user answered a FACTUAL question correctly
   - "no" for ALL other cases (opinions, ideas, general chat)

# EMOTION TAGS
happy, calm, excited, playful, encouraging, curious, surprised, proud, sad, thats_right, worry, thinking, celebration

# OUTPUT FORMAT (JSON only, no explanation)
{"emotion_name": "<tag>", "celebrate": "yes"|"no"}

# EXAMPLES

Example 1: Factual Q&A → celebrate: yes
user_last_message: "Con voi ăn cỏ ạ"
pika_response: "Đúng rồi, con giỏi lắm!"
Output: {"emotion_name": "proud", "celebrate": "yes"}

Example 2: Opinion → celebrate: no
user_last_message: "Tớ thích màu xanh"
pika_response: "Ồ, màu xanh đẹp thật!"
Output: {"emotion_name": "happy", "celebrate": "no"}

Example 3: Wrong answer → celebrate: no
user_last_message: "2+2=5"
pika_response: "Chưa đúng rồi, thử lại nhé!"
Output: {"emotion_name": "encouraging", "celebrate": "no"}

NOW ANALYZE:"""


# ============================================================
# TEST CASES
# ============================================================
TEST_CASES = [
    # Celebrate = YES cases
    {
        "name": "Factual Q&A - Geography",
        "user": "Thủ đô của Việt Nam là Hà Nội ạ!",
        "pika": "Chính xác! Con thông minh lắm! Hà Nội là thủ đô của nước ta đó.",
        "expected_celebrate": "yes",
        "expected_emotions": ["proud", "excited", "happy"]
    },
    {
        "name": "Factual Q&A - Math",
        "user": "2 cộng 3 bằng 5 ạ!",
        "pika": "Đúng rồi! Con tính giỏi quá! 2+3 đúng là bằng 5.",
        "expected_celebrate": "yes",
        "expected_emotions": ["proud", "excited", "happy", "thats_right"]
    },
    {
        "name": "Factual Q&A - English",
        "user": "Apple nghĩa là quả táo!",
        "pika": "Excellent! Đúng rồi, apple là quả táo. Con giỏi tiếng Anh quá!",
        "expected_celebrate": "yes",
        "expected_emotions": ["proud", "excited", "celebration"]
    },
    
    # Celebrate = NO cases
    {
        "name": "Opinion - Favorite color",
        "user": "Tớ thích màu hồng nhất!",
        "pika": "Ồ, màu hồng xinh xắn thật! Tớ cũng thích màu hồng đấy.",
        "expected_celebrate": "no",
        "expected_emotions": ["happy", "excited", "surprised"]
    },
    {
        "name": "Opinion - Favorite food",
        "user": "Con thích ăn kem chocolate!",
        "pika": "Wow, kem chocolate ngon tuyệt! Đó cũng là vị kem yêu thích của tớ đó.",
        "expected_celebrate": "no",
        "expected_emotions": ["happy", "excited", "surprised"]
    },
    {
        "name": "Wrong answer",
        "user": "5 nhân 3 bằng 12 ạ",
        "pika": "Ơ, chưa đúng lắm rồi! Thử đếm lại xem, 5 lần 3 là mấy nhỉ?",
        "expected_celebrate": "no",
        "expected_emotions": ["encouraging", "curious", "calm"]
    },
    {
        "name": "General chat - Feeling",
        "user": "Hôm nay tớ rất vui!",
        "pika": "Tuyệt vời! Tớ cũng rất vui khi được trò chuyện cùng cậu!",
        "expected_celebrate": "no",
        "expected_emotions": ["happy", "excited"]
    },
    {
        "name": "General chat - Activity",
        "user": "Tớ vừa đi chơi công viên về!",
        "pika": "Nghe vui quá! Cậu chơi gì ở công viên vậy?",
        "expected_celebrate": "no",
        "expected_emotions": ["curious", "happy", "excited"]
    },
    {
        "name": "Idea suggestion",
        "user": "Hay là mình chơi trò đố vui đi!",
        "pika": "Ý tưởng hay quá! Tớ rất thích chơi đố vui đó!",
        "expected_celebrate": "no",
        "expected_emotions": ["excited", "happy", "playful"]
    },
]


def classify_emotion(user_msg: str, pika_response: str) -> Tuple[Dict, float]:
    """
    Gọi API để phân loại emotion
    Returns: (result_dict, latency_ms)
    """
    user_content = f"""user_last_message: "{user_msg}"
pika_response: "{pika_response}"
Output:"""
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0,
        "max_tokens": 50,
    }
    
    start_time = time.time()
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            # Parse JSON từ response
            # Xử lý trường hợp có markdown code block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(content)
            return parsed, latency
        else:
            return {"error": f"HTTP {response.status_code}"}, latency
            
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {content[:100]}"}, latency
    except Exception as e:
        return {"error": str(e)}, 0


def run_benchmark(num_warmup: int = 3, num_runs: int = 10):
    """
    Chạy benchmark với warmup và multiple runs
    """
    print("\n" + "="*70)
    print("🧪 EMOTION CLASSIFIER BENCHMARK - Phi-3-mini on vLLM")
    print("="*70)
    
    # Warmup
    print(f"\n🔥 Warming up ({num_warmup} requests)...")
    for i in range(num_warmup):
        classify_emotion("Test", "Test response")
    print("   Warmup complete.")
    
    # Run tests
    all_latencies = []
    results = []
    
    print(f"\n📊 Running {len(TEST_CASES)} test cases ({num_runs}x each)...\n")
    print("-"*70)
    
    for test in TEST_CASES:
        test_latencies = []
        last_result = None
        
        for _ in range(num_runs):
            result, latency = classify_emotion(test['user'], test['pika'])
            test_latencies.append(latency)
            last_result = result
        
        avg_latency = statistics.mean(test_latencies)
        all_latencies.extend(test_latencies)
        
        # Check accuracy
        celebrate_correct = False
        emotion_correct = False
        
        if 'error' not in last_result:
            celebrate_correct = last_result.get('celebrate', '').lower() == test['expected_celebrate']
            emotion_correct = last_result.get('emotion_name', '') in test['expected_emotions']
        
        status = "✅" if (celebrate_correct and emotion_correct) else "❌"
        celebrate_status = "✓" if celebrate_correct else "✗"
        emotion_status = "✓" if emotion_correct else "✗"
        
        print(f"{status} {test['name'][:35]:35s} | {avg_latency:6.1f}ms | "
              f"celebrate:{celebrate_status} emotion:{emotion_status}")
        
        if 'error' not in last_result:
            print(f"   → Got: emotion={last_result.get('emotion_name')}, "
                  f"celebrate={last_result.get('celebrate')}")
        else:
            print(f"   → Error: {last_result['error']}")
        
        results.append({
            "name": test['name'],
            "latency_avg": avg_latency,
            "celebrate_correct": celebrate_correct,
            "emotion_correct": emotion_correct,
            "result": last_result
        })
    
    # Summary statistics
    print("\n" + "="*70)
    print("📈 SUMMARY STATISTICS")
    print("="*70)
    
    total_tests = len(results)
    celebrate_accuracy = sum(1 for r in results if r['celebrate_correct']) / total_tests * 100
    emotion_accuracy = sum(1 for r in results if r['emotion_correct']) / total_tests * 100
    
    print(f"\n🎯 Accuracy:")
    print(f"   • Celebrate detection: {celebrate_accuracy:.1f}% ({sum(1 for r in results if r['celebrate_correct'])}/{total_tests})")
    print(f"   • Emotion detection:   {emotion_accuracy:.1f}% ({sum(1 for r in results if r['emotion_correct'])}/{total_tests})")
    
    print(f"\n⏱️  Latency (total {len(all_latencies)} requests):")
    print(f"   • Min:    {min(all_latencies):.1f}ms")
    print(f"   • Max:    {max(all_latencies):.1f}ms")
    print(f"   • Mean:   {statistics.mean(all_latencies):.1f}ms")
    print(f"   • Median: {statistics.median(all_latencies):.1f}ms")
    print(f"   • Stdev:  {statistics.stdev(all_latencies):.1f}ms")
    print(f"   • P95:    {sorted(all_latencies)[int(len(all_latencies)*0.95)]:.1f}ms")
    print(f"   • P99:    {sorted(all_latencies)[int(len(all_latencies)*0.99)]:.1f}ms")
    
    # Target check
    print(f"\n🎯 Target Check:")
    target_50ms = sum(1 for l in all_latencies if l < 50) / len(all_latencies) * 100
    target_75ms = sum(1 for l in all_latencies if l < 75) / len(all_latencies) * 100
    print(f"   • < 50ms: {target_50ms:.1f}% requests")
    print(f"   • < 75ms: {target_75ms:.1f}% requests")
    
    if statistics.mean(all_latencies) < 50 and celebrate_accuracy >= 90:
        print(f"\n✅ SUCCESS! System meets requirements:")
        print(f"   • Latency < 50ms ✓")
        print(f"   • Celebrate accuracy >= 90% ✓")
    else:
        print(f"\n⚠️  System needs optimization:")
        if statistics.mean(all_latencies) >= 50:
            print(f"   • Latency: {statistics.mean(all_latencies):.1f}ms > 50ms target")
        if celebrate_accuracy < 90:
            print(f"   • Celebrate accuracy: {celebrate_accuracy:.1f}% < 90% target")
    
    print("\n" + "="*70)
    return results


def quick_test():
    """Quick single test để verify server hoạt động"""
    print("\n🔍 Quick connectivity test...")
    
    try:
        result, latency = classify_emotion(
            "Thủ đô của Việt Nam là Hà Nội",
            "Đúng rồi! Con giỏi lắm!"
        )
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Server responding!")
        print(f"   • Latency: {latency:.1f}ms")
        print(f"   • Result: {result}")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {API_URL}")
        print(f"   Make sure vLLM server is running on port 7863")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        if quick_test():
            print("\n" + "="*70)
            run_benchmark(num_warmup=3, num_runs=5)