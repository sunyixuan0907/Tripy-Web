from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'data.db'}"