# Emotion Classification Service

Service FastAPI dùng Groq để gắn nhãn cảm xúc và quyết định celebrate, trả về text ngắn để giảm độ trễ.

## Chạy nhanh
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # điền GROQ_API_KEY
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 30031
```

## Biến môi trường
- `GROQ_API_KEY` (bắt buộc)
- `GROQ_MODEL` (mặc định: openai/gpt-oss-20b)

## Thư mục chính
- `src/` code dịch vụ (api, services, clients, prompts, models, core, utils)
- `tests/` (chưa thêm)
# VeryFastMoodEmotionClassification_T12_2025
VeryFastMoodEmotionClassification_T12_2025
