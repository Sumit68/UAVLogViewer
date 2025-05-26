# run_hyper.py
from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio
from main import app

config = Config()
config.bind = ["127.0.0.1:8000"]
config.reload = True
config.limit_max_request_size = 100 * 1024 * 1024  # 100MB

if __name__ == "__main__":
    asyncio.run(serve(app, config))
