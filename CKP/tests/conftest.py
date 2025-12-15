"""
Pytest configuration và fixtures chung cho tất cả tests.

- Load .env file trước khi chạy tests
- Configure pytest-asyncio (via pyproject.toml)
"""

from pathlib import Path

from dotenv import load_dotenv


# Load .env file từ project root
def pytest_configure(config):
    """Load .env file trước khi chạy tests."""
    # Tìm .env file từ project root
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        load_dotenv(env_file, override=False)
        print(f"✅ Loaded .env file from: {env_file}")
    else:
        print(f"⚠️  .env file not found at: {env_file}")
        # Thử load từ current directory
        load_dotenv(override=False)

