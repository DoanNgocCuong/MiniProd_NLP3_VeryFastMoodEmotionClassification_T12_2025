#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re
from pathlib import Path
from datetime import datetime

def parse_user_input(user_input_text):
    """
    Parse user_input text thành 3 phần: previous_pika_question, user_answer, now_pika_response
    
    Format: "Previous Robot Pika's Question: {previous_pika_question}\n Previous Children's Answer: {user_answer}\n Now Pika Robot's Response need check: {now_pika_response}"
    
    Args:
        user_input_text (str): Text cần parse
        
    Returns:
        tuple: (previous_pika_question, user_answer, now_pika_response)
    """
    if pd.isna(user_input_text) or not isinstance(user_input_text, str):
        return None, None, None
    
    # Pattern để extract các phần - xử lý cả "Children's" và "Children 's" (có dấu cách)
    # Sử dụng non-greedy match và xử lý cả trường hợp có/không có dấu cách sau \n
    pattern = r"Previous Robot Pika's Question:\s*(.*?)\n\s*Previous Children\s*'s Answer:\s*(.*?)\n\s*Now Pika Robot's Response need check:\s*(.*?)$"
    
    match = re.search(pattern, user_input_text, re.DOTALL)
    
    if match:
        previous_pika_question = match.group(1).strip()
        user_answer = match.group(2).strip()
        now_pika_response = match.group(3).strip()
        return previous_pika_question, user_answer, now_pika_response
    else:
        # Fallback: thử split theo \n nếu regex không match
        lines = user_input_text.split('\n')
        previous_pika_question = None
        user_answer = None
        now_pika_response = None
        
        for line in lines:
            if "Previous Robot Pika's Question:" in line:
                previous_pika_question = line.split("Previous Robot Pika's Question:")[-1].strip()
            elif "Previous Children" in line and "'s Answer:" in line:
                # Xử lý cả "Children's" và "Children 's"
                parts = re.split(r"Previous Children\s*'s Answer:", line)
                if len(parts) > 1:
                    user_answer = parts[-1].strip()
            elif "Now Pika Robot's Response need check:" in line:
                now_pika_response = line.split("Now Pika Robot's Response need check:")[-1].strip()
        
        return previous_pika_question, user_answer, now_pika_response


def process_excel_file(input_file_path, output_file_path=None):
    """
    Đọc file Excel, parse cột user_input và tạo file output với 3 cột mới
    
    Args:
        input_file_path (str): Đường dẫn đến file Excel input
        output_file_path (str, optional): Đường dẫn file output. Nếu None, tự động tạo tên
    """
    # Đọc file Excel
    print(f"📖 Đang đọc file: {input_file_path}")
    try:
        df = pd.read_excel(input_file_path)
        print(f"✅ Đã đọc thành công {len(df)} dòng")
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {e}")
        return
    
    # Kiểm tra cột user_input
    if 'user_input' not in df.columns:
        print(f"❌ Không tìm thấy cột 'user_input'")
        print(f"📋 Các cột có sẵn: {df.columns.tolist()}")
        return
    
    # Parse từng dòng và tạo DataFrame mới
    print("🔄 Đang parse dữ liệu...")
    parsed_data = []
    
    for index, row in df.iterrows():
        user_input = row['user_input']
        previous_pika_question, user_answer, now_pika_response = parse_user_input(user_input)
        
        parsed_data.append({
            'index': index,  # Giữ index gốc
            'previous_pika_question': previous_pika_question,
            'user_answer': user_answer,
            'now_pika_response': now_pika_response
        })
    
    # Tạo DataFrame mới với 4 cột: index + 3 cột parsed
    df_output = pd.DataFrame(parsed_data)
    
    # Tạo tên file output nếu chưa có
    if output_file_path is None:
        input_path = Path(input_file_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file_path = input_path.parent / f"{input_path.stem}_parsed_{timestamp}.xlsx"
    
    # Lưu file output
    print(f"💾 Đang lưu file output: {output_file_path}")
    try:
        df_output.to_excel(output_file_path, index=False)
        print(f"✅ Đã lưu thành công vào: {output_file_path}")
        print(f"📊 Số dòng đã xử lý: {len(df_output)}")
        
        # Thống kê
        print("\n📈 Thống kê:")
        print(f"  - Tổng số dòng: {len(df_output)}")
        print(f"  - Dòng có previous_pika_question: {df_output['previous_pika_question'].notna().sum()}")
        print(f"  - Dòng có user_answer: {df_output['user_answer'].notna().sum()}")
        print(f"  - Dòng có now_pika_response: {df_output['now_pika_response'].notna().sum()}")
        
    except Exception as e:
        print(f"❌ Lỗi khi lưu file: {e}")
        return
    
    return df_output


def main():
    """Hàm main để chạy script"""
    # Đường dẫn file input
    input_file = r"D:\GIT\VeryFastMoodEmotionClassification_T12_2025\data\data.xlsx"
    
    # Xử lý file
    result_df = process_excel_file(input_file)
    
    if result_df is not None:
        print("\n✅ Hoàn thành!")
        print(f"📋 Preview 5 dòng đầu:")
        print(result_df.head())


if __name__ == "__main__":
    main()

