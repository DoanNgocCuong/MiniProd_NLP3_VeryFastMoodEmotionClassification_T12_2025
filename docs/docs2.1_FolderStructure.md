# 📁 Emotion Classification Service - Folder Structure

```
emotion-classifier-service/
│
├── 📄 README.md                     # Project documentation
├── 📄 requirements.txt              # Python dependencies
├── 📄 pyproject.toml                # Modern Python project config
├── 📄 .env.example                  # Environment variables template
├── 📄 .gitignore                    # Git ignore rules
├── 📄 Dockerfile                    # Container deployment
├── 📄 docker-compose.yml            # Local dev orchestration
│
├── 📁 src/                          # Main source code
│   ├── 📄 __init__.py
│   │
│   ├── 📁 api/                      # FastAPI endpoints
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py               # FastAPI app entry point
│   │   ├── 📄 routes.py             # API route definitions
│   │   ├── 📄 dependencies.py       # Dependency injection
│   │   └── 📄 middleware.py         # Request/response middleware
│   │
│   ├── 📁 services/                 # Business logic layer
│   │   ├── 📄 __init__.py
│   │   ├── 📄 emotion_service.py    # Emotion detection logic
│   │   ├── 📄 celebrate_service.py  # Celebrate decision logic
│   │   └── 📄 combined_service.py   # Parallel execution of both
│   │
│   ├── 📁 clients/                  # External API clients
│   │   ├── 📄 __init__.py
│   │   ├── 📄 groq_client.py        # Groq API wrapper (sync)
│   │   └── 📄 groq_client_async.py  # Groq API wrapper (async)
│   │
│   ├── 📁 prompts/                  # LLM prompts (separated for easy tuning)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 emotion_prompt.py     # Emotion detection prompt
│   │   └── 📄 celebrate_prompt.py   # Celebrate detection prompt
│   │
│   ├── 📁 models/                   # Pydantic models (request/response schemas)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 requests.py           # Input schemas
│   │   ├── 📄 responses.py          # Output schemas
│   │   └── 📄 enums.py              # Emotion enum definitions
│   │
│   ├── 📁 core/                     # Core configurations
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py             # Settings & environment variables
│   │   ├── 📄 constants.py          # Static constants
│   │   └── 📄 exceptions.py         # Custom exceptions
│   │
│   └── 📁 utils/                    # Utility functions
│       ├── 📄 __init__.py
│       ├── 📄 json_parser.py        # Safe JSON parsing
│       ├── 📄 timing.py             # Performance timing decorators
│       └── 📄 logging.py            # Structured logging setup
│
├── 📁 tests/                        # Test suite
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py               # Pytest fixtures
│   │
│   ├── 📁 unit/                     # Unit tests
│   │   ├── 📄 test_emotion_service.py
│   │   ├── 📄 test_celebrate_service.py
│   │   └── 📄 test_prompts.py
│   │
│   ├── 📁 integration/              # Integration tests
│   │   ├── 📄 test_groq_client.py
│   │   └── 📄 test_api_endpoints.py
│   │
│   └── 📁 fixtures/                 # Test data
│       ├── 📄 sample_conversations.json
│       └── 📄 expected_outputs.json
│
├── 📁 scripts/                      # Utility scripts
│   ├── 📄 benchmark.py              # Latency benchmarking
│   ├── 📄 test_groq_connection.py   # Connection test
│   └── 📄 generate_test_data.py     # Generate test cases
│
├── 📁 docs/                         # Documentation
│   ├── 📄 API.md                    # API documentation
│   ├── 📄 PROMPTS.md                # Prompt engineering notes
│   └── 📄 DEPLOYMENT.md             # Deployment guide
│
└── 📁 deployment/                   # Deployment configs
    ├── 📁 k8s/                      # Kubernetes manifests
    │   ├── 📄 deployment.yaml
    │   ├── 📄 service.yaml
    │   └── 📄 configmap.yaml
    │
    └── 📁 terraform/                # Infrastructure as Code (optional)
        └── 📄 main.tf
```

---

## 📄 Key Files Content Preview

### `src/models/enums.py`
```python
from enum import Enum

class EmotionName(str, Enum):
    HAPPY = "happy"
    CALM = "calm"
    EXCITED = "excited"
    PLAYFUL = "playful"
    NO_PROBLEM = "no_problem"
    ENCOURAGING = "encouraging"
    CURIOUS = "curious"
    SURPRISED = "surprised"
    PROUD = "proud"
    IDLE = "idle"
    SAD = "sad"
    THATS_RIGHT = "thats_right"
    WORRY = "worry"
    THINKING = "thinking"

class CelebrateDecision(str, Enum):
    YES = "yes"
    NO = "no"
```

### `src/models/requests.py`
```python
from pydantic import BaseModel, Field

class EmotionRequest(BaseModel):
    user_last_message: str = Field(..., description="Last message from user/child")
    pika_response: str = Field(..., description="Robot's response to classify")

class CelebrateRequest(BaseModel):
    user_last_message: str
    pika_response: str

class CombinedRequest(BaseModel):
    user_last_message: str
    pika_response: str
```

### `src/models/responses.py`
```python
from pydantic import BaseModel
from .enums import EmotionName, CelebrateDecision

class EmotionResponse(BaseModel):
    emotion_name: EmotionName
    latency_ms: float

class CelebrateResponse(BaseModel):
    celebrate: CelebrateDecision
    latency_ms: float

class CombinedResponse(BaseModel):
    emotion_name: EmotionName
    celebrate: CelebrateDecision
    total_latency_ms: float
```

### `src/prompts/emotion_prompt.py`
```python
SYSTEM_PROMPT = """You are an ultra-fast JSON API that detects the emotion in a robot's response.
- Analyze the robot's `pika_response` within the `user_last_message` context.
- Pick the single most fitting emotion from the list.
- Respond ONLY with a valid JSON object: {"emotion_name": "..."}

EMOTION LIST:
'happy', 'calm', 'excited', 'playful', 'no_problem', 'encouraging', 'curious', 'surprised', 'proud', 'idle', 'sad', 'thats_right', 'worry', 'thinking'
"""

def build_user_prompt(user_last_message: str, pika_response: str) -> str:
    return f"""
[CONTEXT]
user_last_message: "{user_last_message}"
pika_response: "{pika_response}"

[YOUR JSON OUTPUT]
"""
```

### `src/prompts/celebrate_prompt.py`
```python
SYSTEM_PROMPT = """You are an ultra-fast JSON API, a binary classifier for a robot's celebration action.
- `celebrate` is "yes" ONLY IF the `pika_response` confirms the user correctly answered a factual, objective question.
- In ALL other cases (opinions, ideas, feelings, wrong answers), `celebrate` is "no".
- Respond ONLY with a valid JSON object: {"celebrate": "yes" | "no"}
"""

def build_user_prompt(user_last_message: str, pika_response: str) -> str:
    return f"""
[CONTEXT]
user_last_message: "{user_last_message}"
pika_response: "{pika_response}"

[YOUR JSON OUTPUT]
"""
```

### `src/core/config.py`
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Groq Configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    GROQ_TIMEOUT: float = 10.0
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 30031
    DEBUG: bool = False
    
    # Performance
    MAX_TOKENS_EMOTION: int = 50
    MAX_TOKENS_CELEBRATE: int = 20
    TEMPERATURE: float = 0.0
    TOP_P: float = 0.1
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### `src/api/routes.py`
```python
from fastapi import APIRouter, Depends
from ..models.requests import EmotionRequest, CelebrateRequest, CombinedRequest
from ..models.responses import EmotionResponse, CelebrateResponse, CombinedResponse
from ..services.emotion_service import EmotionService
from ..services.celebrate_service import CelebrateService
from ..services.combined_service import CombinedService

router = APIRouter(prefix="/api/v1", tags=["Classification"])

@router.post("/emotion", response_model=EmotionResponse)
async def classify_emotion(
    request: EmotionRequest,
    service: EmotionService = Depends()
):
    return await service.classify(request)

@router.post("/celebrate", response_model=CelebrateResponse)
async def detect_celebrate(
    request: CelebrateRequest,
    service: CelebrateService = Depends()
):
    return await service.classify(request)

@router.post("/classify", response_model=CombinedResponse)
async def classify_combined(
    request: CombinedRequest,
    service: CombinedService = Depends()
):
    """Parallel execution of both classifiers"""
    return await service.classify_parallel(request)
```

### `src/clients/groq_client_async.py`
```python
import asyncio
from groq import AsyncGroq
from ..core.config import get_settings

class AsyncGroqClient:
    def __init__(self):
        settings = get_settings()
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.timeout = settings.GROQ_TIMEOUT
    
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 50
    ) -> str:
        settings = get_settings()
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=settings.TEMPERATURE,
            max_tokens=max_tokens,
            top_p=settings.TOP_P,
            response_format={"type": "json_object"},
        )
        
        return response.choices[0].message.content
```

### `src/services/combined_service.py`
```python
import asyncio
import time
from ..models.requests import CombinedRequest
from ..models.responses import CombinedResponse
from .emotion_service import EmotionService
from .celebrate_service import CelebrateService

class CombinedService:
    def __init__(self):
        self.emotion_service = EmotionService()
        self.celebrate_service = CelebrateService()
    
    async def classify_parallel(self, request: CombinedRequest) -> CombinedResponse:
        """Execute both classifications in parallel"""
        start_time = time.perf_counter()
        
        # Run both API calls concurrently
        emotion_task = self.emotion_service.classify(request)
        celebrate_task = self.celebrate_service.classify(request)
        
        emotion_result, celebrate_result = await asyncio.gather(
            emotion_task,
            celebrate_task
        )
        
        total_latency = (time.perf_counter() - start_time) * 1000
        
        return CombinedResponse(
            emotion_name=emotion_result.emotion_name,
            celebrate=celebrate_result.celebrate,
            total_latency_ms=total_latency
        )
```

---

## 🚀 Quick Start Commands

```bash
# 1. Clone and setup
git clone <repo>
cd emotion-classifier-service

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run development server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 30031

# 6. Run tests
pytest tests/ -v

# 7. Benchmark
python scripts/benchmark.py
```

---

## 📦 requirements.txt

```
# Core
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.7.0
pydantic-settings>=2.0.0

# Groq Client
groq>=0.9.0

# Async support
httpx>=0.27.0
aiohttp>=3.9.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0

# Development
python-dotenv>=1.0.0
```