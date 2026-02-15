import uvicorn
from src.app import app

uvicorn.run(app, port=8000)
