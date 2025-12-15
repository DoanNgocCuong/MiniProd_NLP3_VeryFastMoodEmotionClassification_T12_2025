#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
import time
from datetime import datetime

# Configuration
API_URL = "http://103.253.20.30:30030/v1/chat/completions"
API_MODEL = "Qwen/Qwen2.5-1.5B-Instruct-AWQ"
SYSTEM_PROMPT = (
    "You are an emotion classifier for Pika Robot's responses.\n"
    "Task:\n"
    "* Read the conversation snippet.\n"
    "* Focus ONLY on \"Now Pika Robot's Response need check\" and identify the MAIN emotion expressed in that turn.\n"
    "Emotion rules: Choose exactly ONE emotion from this list and output only that word: "
    "happy, calm, excited, playful, no_problem, encouraging, curious, surprised, proud, "
    "thats_right, sad, angry, worry, afraid, noisy, thinking"
)
SYSTEM_PROMPT = "You are an expert emotion classifier. Output EXACTLY ONE emotion label - nothing else.\n\nCLASSIFICATION RULES (apply in strict order - FIRST MATCH WINS):\n\n1. NO_PROBLEM (reassurance after mistake or learning together):\n   Keywords: \"Sai chút\", \"không sao\", \"No worries\", \"Don't worry\", \"Không sao\", \"Đừng lo\", \"lần sau\", \"cố gắng hơn\", \"cùng nhau\"\n   → output: no_problem\n\n2. THATS_RIGHT (confirmation of correct answer):\n   Keywords: \"Excellent\", \"Awesome\", \"Fantastic\", \"Bravo\", \"Great job\", \"Amazing\", \"Well done\", \"Đúng rồi\", \"Cậu đã nói đúng\"\n   → output: thats_right\n\n3. PROUD (recognition of achievement):\n   Keywords: \"proud\", \"Giỏi lắm\", \"did it\", \"Yay\", \"So proud\"\n   → output: proud\n\n4. ENCOURAGING (motivation to continue/improve):\n   Keywords: \"Keep it up\", \"Let's go\", \"Giờ nhanh hơn\", \"faster\", \"Cuối cùng\", \"tốc độ người bản ngữ\", \"tiếp tục\", \"tiếp nào\"\n   → output: encouraging\n\n5. HAPPY (general positive/celebratory):\n   Keywords: \"High five\", \"Nice work\", \"Chúng ta tiếp tục\"\n   → output: happy\n\n6. THINKING (empty or no keywords match):\n   → output: thinking\n\nIMPORTANT: Output ONLY the emotion label in lowercase. No explanation, no extra text."
# SYSTEM_PROMPT = "Classify emotion. Output ONE label only.\n\nEmotions: happy happy_2 calm excited excited_2 playful playful_2 playful_3 no_problem encouraging encouraging_2 curious surprised proud proud_2 idle sad thats_right thats_right_2 angry worry afraid noisy celebration thinking\n\nRules:\n- Excellent/Awesome/Fantastic/Bravo/Amazing/Well done → celebration\n- Đúng rồi/Cậu đã nói đúng → thats_right\n- Giỏi lắm/did it/Yay/So proud → proud\n- Keep it up/Let's go/Giờ nhanh hơn/faster/Cuối cùng/tiếp tục → encouraging\n- Sai chút/không sao/No worries/Đừng lo/lần sau → no_problem\n- High five/Nice work/Chúng ta tiếp tục → happy\n- Empty or unclear → thinking\n\nOutput: [emotion label]"

# Input configuration (dùng giống celebrate_benchmark: chỉ cần cột user_input)
EXCEL_FILE = "../result_all_rows_type1.xlsx"
DATA_COLUMN = "user_input"
ID_COLUMN = "id"


def build_user_message(content: str) -> str:
    """Compose the user message payload for the classifier (single column)."""
    return content


def run_emotion_benchmark(sample_size: int | None = 10):
    """Run emotion-classification benchmark."""
    print("🚀 Starting Emotion Classification Benchmark")
    print(f"📊 Sample size: {sample_size if sample_size is not None else 'FULL'}")
    print(f"🔗 API URL: {API_URL}")
    print("-" * 50)

    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"📁 Loaded {len(df)} rows from Excel")
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return

    if DATA_COLUMN not in df.columns:
        print(f"❌ Column '{DATA_COLUMN}' not found in Excel")
        print(f"Available columns: {df.columns.tolist()}")
        return

    if ID_COLUMN not in df.columns:
        print(f"⚠️  Column '{ID_COLUMN}' not found. Using row index as id.")
        df[ID_COLUMN] = df.index + 1

    df_filtered = df[[ID_COLUMN, DATA_COLUMN]].dropna(subset=[DATA_COLUMN])

    if sample_size is None:
        df_test = df_filtered.copy()
    else:
        df_test = df_filtered.sort_values(ID_COLUMN).head(sample_size)

    test_data = df_test[[ID_COLUMN, DATA_COLUMN]].values.tolist()

    print(f"📋 Processing {len(test_data)} samples")
    print(f"📌 ID range: {df_test[ID_COLUMN].min()} - {df_test[ID_COLUMN].max()}")

    results = []
    start_time = time.time()

    for i, (row_id, content) in enumerate(test_data, 1):
        print(f"⏳ Processing {i}/{len(test_data)} (ID: {row_id})... ", end="")

        payload = {
            "model": API_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_message(content)},
            ],
            "temperature": 0,
            "max_tokens": 5,
            "stop": ["\n", " ", ".", ","],
        }

        try:
            req_start = time.time()
            response = requests.post(
                API_URL,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            req_end = time.time()
            response_time = req_end - req_start

            if response.status_code == 200:
                try:
                    response_json = response.json()
                    classification = response_json["choices"][0]["message"]["content"].strip()
                    results.append(
                        {
                            "id": row_id,
                            "index": i,
                            "status": "success",
                            "classification": classification,
                            "response_time": response_time,
                            "content": content,
                        }
                    )
                    print(f"✅ {classification} ({response_time*1000:.0f}ms)")
                except Exception:
                    results.append(
                        {
                            "id": row_id,
                            "index": i,
                            "status": "json_error",
                            "classification": "error",
                            "response_time": response_time,
                            "error_detail": response.text[:500],
                        }
                    )
                    print(f"❌ JSON Error ({response_time*1000:.0f}ms)")
            else:
                err_text = response.text.strip()
                results.append(
                    {
                        "id": row_id,
                        "index": i,
                        "status": f"http_{response.status_code}",
                        "classification": "error",
                        "response_time": response_time,
                        "content": content,
                        "error_detail": err_text[:500],
                    }
                )
                print(f"❌ HTTP {response.status_code} ({response_time*1000:.0f}ms) {err_text[:120]}")

        except requests.exceptions.Timeout:
            results.append(
                {
                    "id": row_id,
                    "index": i,
                    "status": "timeout",
                    "classification": "timeout",
                    "response_time": 30,
                    "content": content,
                }
            )
            print("⏰ Timeout")

        except Exception as e:
            results.append(
                {
                    "id": row_id,
                    "index": i,
                    "status": "error",
                    "classification": "error",
                    "response_time": 0,
                    "content": content,
                    "error_detail": str(e)[:500],
                }
            )
            print(f"❌ Error: {str(e)}")

        time.sleep(0.1)

    end_time = time.time()
    total_time = end_time - start_time

    total_requests = len(results)
    successful = len([r for r in results if r["status"] == "success"])
    error_count = total_requests - successful
    avg_response_time = (
        sum(r["response_time"] for r in results) / total_requests if total_requests > 0 else 0
    )

    # Label distribution
    label_counts = {}
    for r in results:
        label = r.get("classification")
        if label:
            label_counts[label] = label_counts.get(label, 0) + 1

    print("\n" + "=" * 50)
    print("📈 BENCHMARK RESULTS")
    print("=" * 50)
    print(f"⏱️  Total Time: {total_time:.2f} seconds")
    print(f"📊 Requests/Second: {total_requests/total_time:.2f}")
    print(f"✅ Success Rate: {successful}/{total_requests} ({(successful/total_requests)*100:.1f}%)")
    print(f"⚡ Avg Response Time: {avg_response_time*1000:.0f} ms")
    print("🎯 Label distribution:")
    for label, count in sorted(label_counts.items(), key=lambda x: x[0]):
        print(f"   {label}: {count} ({(count/total_requests)*100:.1f}%)")
    print(f"   errors: {error_count} ({(error_count/total_requests)*100:.1f}%)")

    # Save results to Excel
    results_df = pd.DataFrame(results).sort_values("id").reset_index(drop=True)
    output_file = f"emotion_benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        results_df.to_excel(writer, sheet_name="Results", index=False)

        summary_data = {
            "Metric": [
                "Total Requests",
                "Successful",
                "Success Rate %",
                "Total Time (s)",
                "Requests/Second",
                "Avg Response Time (ms)",
                "Error Count",
            ],
            "Value": [
                total_requests,
                successful,
                (successful / total_requests) * 100 if total_requests else 0,
                total_time,
                total_requests / total_time if total_time else 0,
                avg_response_time * 1000,
                error_count,
            ],
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        labels_df = pd.DataFrame(
            [{"label": label, "count": count, "percent": (count / total_requests) * 100}]
            for label, count in label_counts.items()
        )
        labels_df.to_excel(writer, sheet_name="LabelDistribution", index=False)

    print(f"\n💾 Results saved to: {output_file}")
    return results


def main():
    print("🤖 Emotion Classification Benchmark Tool")
    print("Choose an option:")
    print("1. Quick test (10 samples)")
    print("2. Medium test (200 samples)")
    print("3. Large test (1000 samples)")
    print("4. Full dataset")
    print("5. Custom size")

    try:
        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            sample_size = 10
        elif choice == "2":
            sample_size = 200
        elif choice == "3":
            sample_size = 1000
        elif choice == "4":
            sample_size = None  # Full dataset
        elif choice == "5":
            sample_size = int(input("Enter sample size: "))
        else:
            print("❌ Invalid choice")
            return

        run_emotion_benchmark(sample_size)

    except KeyboardInterrupt:
        print("\n\n🛑 Benchmark stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

