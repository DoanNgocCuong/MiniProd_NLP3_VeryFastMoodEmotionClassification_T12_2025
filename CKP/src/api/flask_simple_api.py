"""
Ultra-simple Flask API - match chính xác code test1.py.
Tham khảo pattern từ Flask code mẫu (45ms).

Đặc điểm:
- Load client ngay khi module load (global variable)
- Không có overhead, không có wrapper phức tạp
- Match chính xác code test1.py
"""
import os
import time
from flask import Flask, request, jsonify

from groq import Groq

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables - load ngay khi module load (như code mẫu)
API_KEY = os.getenv("GROQ_API_KEY", "")

# Load client ngay khi module load - không có overhead
logger.info("Loading Groq client...")
client = Groq(api_key=API_KEY)
logger.info("Groq client loaded successfully")

# Flask app
app = Flask(__name__)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "client_loaded": client is not None
    })

@app.route('/celebrate', methods=['POST'])
def classify_celebrate():
    """
    Classify celebrate - siêu đơn giản, match chính xác test1.py.
    
    Request body:
    {
        "input": "Previous Question: ... Previous Answer: ... Response to check: ..."
    }
    
    Response:
    {
        "celebrate": "yes" | "no",
        "latency_ms": float
    }
    """
    try:
        # Parse request
        data = request.json
        if not data or 'input' not in data:
            return jsonify({"error": "Missing 'input' field"}), 400
        
        user_input = data['input']
        
        # Start timing - match test1.py
        start_time = time.time()
        
        # Call Groq API - match chính xác test1.py
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "· 'celebrate' is \"yes\" ONLY IF the 'pika_response' confirms the user correctly\n  answered a factual, objective question.\n· In ALL other cases (opinions, ideas, feelings, wrong answers), 'celebrate' is\n  \"no\".\n· Respond ONLY text: yes/no\n"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0,
            max_completion_tokens=512,
            top_p=1,
            stream=False,
            stop=None
        )
        
        # End timing - match test1.py
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Parse result
        result = (completion.choices[0].message.content or "no").strip().lower()
        celebrate = "yes" if result == "yes" else "no"
        
        logger.info(f"Prediction completed in {response_time:.2f}ms - Result: {celebrate}")
        
        return jsonify({
            "celebrate": celebrate,
            "latency_ms": round(response_time, 2)
        })
        
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint."""
    return jsonify({
        "message": "Simple Groq Flask API",
        "endpoint": "/celebrate",
        "status": "running"
    })

if __name__ == "__main__":
    # Production setup message
    logger.info("Starting Flask API server on 0.0.0.0:30029")
    logger.info("For production deployment, use: gunicorn -w 4 -b 0.0.0.0:30029 -t 60 flask_simple_api:app")
    
    # Development mode
    app.run(host="0.0.0.0", port=30029, debug=False, threaded=True)

