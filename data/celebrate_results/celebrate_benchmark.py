#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
import time
import json
from datetime import datetime

# Configuration
API_URL = "http://103.253.20.30:30030/v1/chat/completions"
API_MODEL = "Qwen/Qwen2.5-1.5B-Instruct-AWQ"
SYSTEM_PROMPT = "CLASSIFY: 'yes' if Pika's response confirms a correct factual answer. Otherwise, 'no'. Output ONLY 'yes' or 'no'."
SYSTEM_PROMPT = "Classify Pika's response (response to check) as 'yes' or 'no'.\nyes = Pika celebrates a correct answer\nno = opinion, feeling, or wrong answer\n\nExamples:\n- 'Yeahhh! Cậu làm đúng rồi!' → yes\n- 'Perfect! I got it right!' → yes\n- 'I think this lesson is interesting' → no\n- 'Tớ hơi mệt rồi' → no\n\nOutput ONLY 'yes' or 'no'."
EXCEL_FILE = "result_all_rows.xlsx"  # Đường dẫn đến file Excel của bạn
DATA_COLUMN = "user_input"

def run_simple_benchmark(sample_size=10):
    """Run a simple benchmark test"""
    print("🚀 Starting Classification Benchmark")
    print(f"📊 Sample size: {sample_size}")
    print(f"🔗 API URL: {API_URL}")
    print("-" * 50)
    
    # Load data
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"📁 Loaded {len(df)} rows from Excel")
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")
        return
    
    # Check for data column
    if DATA_COLUMN not in df.columns:
        print(f"❌ Column '{DATA_COLUMN}' not found in Excel")
        print(f"Available columns: {df.columns.tolist()}")
        return
    
    # Check for id column
    ID_COLUMN = 'id'
    if ID_COLUMN not in df.columns:
        print(f"⚠️  Column '{ID_COLUMN}' not found in Excel")
        print(f"Available columns: {df.columns.tolist()}")
        print("⚠️  Will use row index as id")
        df[ID_COLUMN] = df.index + 1
    
    # Sample data for testing - lấy theo cột id
    df_filtered = df[[ID_COLUMN, DATA_COLUMN]].dropna(subset=[DATA_COLUMN])
    
    if sample_size is None:
        df_test = df_filtered.copy()
    else:
        # Lấy sample_size dòng đầu tiên theo thứ tự id
        df_test = df_filtered.sort_values(ID_COLUMN).head(sample_size)
    
    # Tạo list với id và content
    test_data = df_test[[ID_COLUMN, DATA_COLUMN]].values.tolist()
    
    print(f"📋 Processing {len(test_data)} samples")
    print(f"📌 ID range: {df_test[ID_COLUMN].min()} - {df_test[ID_COLUMN].max()}")
    
    results = []
    start_time = time.time()
    
    for i, (row_id, content) in enumerate(test_data, 1):
        print(f"⏳ Processing {i}/{len(test_data)} (ID: {row_id})... ", end="")
        
        # Prepare request
        payload = {
            "model": API_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content}
            ],
            "temperature": 0,
            "max_tokens": 1,
            "stop": ["\n", " ", ".", ","]
        }
        
        # Make request
        try:
            req_start = time.time()
            response = requests.post(
                API_URL,
                headers={'Content-Type': 'application/json'},
                json=payload,
                timeout=30
            )
            req_end = time.time()
            response_time = req_end - req_start
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    classification = response_json['choices'][0]['message']['content'].strip()
                    results.append({
                        'id': row_id,
                        'index': i,
                        'status': 'success',
                        'classification': classification,
                        'response_time': response_time,
                        'content': content
                    })
                    print(f"✅ {classification} ({response_time*1000:.0f}ms)")
                except:
                    results.append({
                        'id': row_id,
                        'index': i,
                        'status': 'json_error',
                        'classification': 'error',
                        'response_time': response_time,
                        'content': content
                    })
                    print(f"❌ JSON Error ({response_time*1000:.0f}ms)")
            else:
                results.append({
                    'id': row_id,
                    'index': i,
                    'status': f'http_{response.status_code}',
                    'classification': 'error',
                    'response_time': response_time,
                    'content': content
                })
                print(f"❌ HTTP {response.status_code} ({response_time*1000:.0f}ms)")
                
        except requests.exceptions.Timeout:
            results.append({
                'id': row_id,
                'index': i,
                'status': 'timeout',
                'classification': 'timeout',
                'response_time': 30,
                'content': content
            })
            print(f"⏰ Timeout")
            
        except Exception as e:
            results.append({
                'id': row_id,
                'index': i,
                'status': 'error',
                'classification': 'error',
                'response_time': 0,
                'content': content
            })
            print(f"❌ Error: {str(e)}")
        
        # Small delay to avoid overwhelming server
        time.sleep(0.1)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate statistics
    total_requests = len(results)
    successful = len([r for r in results if r['status'] == 'success'])
    yes_count = len([r for r in results if r['classification'] == 'yes'])
    no_count = len([r for r in results if r['classification'] == 'no'])
    error_count = total_requests - successful
    
    avg_response_time = sum(r['response_time'] for r in results) / total_requests if total_requests > 0 else 0
    
    # Print results
    print("\n" + "="*50)
    print("📈 BENCHMARK RESULTS")
    print("="*50)
    print(f"⏱️  Total Time: {total_time:.2f} seconds")
    print(f"📊 Requests/Second: {total_requests/total_time:.2f}")
    print(f"✅ Success Rate: {successful}/{total_requests} ({(successful/total_requests)*100:.1f}%)")
    print(f"⚡ Avg Response Time: {avg_response_time*1000:.0f} ms")
    print(f"🎯 Classifications:")
    print(f"   'yes': {yes_count} ({(yes_count/total_requests)*100:.1f}%)")
    print(f"   'no':  {no_count} ({(no_count/total_requests)*100:.1f}%)")
    print(f"   errors: {error_count} ({(error_count/total_requests)*100:.1f}%)")
    
    # Save results to Excel
    results_df = pd.DataFrame(results)
    # Sort theo id để giữ đúng thứ tự theo id của file input
    results_df = results_df.sort_values('id').reset_index(drop=True)
    output_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        results_df.to_excel(writer, sheet_name='Results', index=False)
        
        # Summary sheet
        summary_data = {
            'Metric': ['Total Requests', 'Successful', 'Success Rate %', 'Total Time (s)', 
                      'Requests/Second', 'Avg Response Time (ms)', 'Yes Count', 'No Count', 'Error Count'],
            'Value': [total_requests, successful, (successful/total_requests)*100, total_time,
                     total_requests/total_time, avg_response_time*1000, yes_count, no_count, error_count]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    return results

def main():
    print("🤖 Classification API Benchmark Tool")
    print("Choose an option:")
    print("1. Quick test (10 samples)")
    print("2. Medium test (200 samples)")
    print("3. Large test (1000 samples)")
    print("4. Full dataset")
    print("5. Custom size")
    
    try:
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            sample_size = 10
        elif choice == '2':
            sample_size = 200
        elif choice == '3':
            sample_size = 1000
        elif choice == '4':
            sample_size = None  # Full dataset
        elif choice == '5':
            sample_size = int(input("Enter sample size: "))
        else:
            print("❌ Invalid choice")
            return
        
        run_simple_benchmark(sample_size)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Benchmark stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()