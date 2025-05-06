import argparse
import os

import uvicorn

from app import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=os.getenv("PORT", 8000), type=int)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
