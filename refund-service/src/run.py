#!/usr/bin/env python3
"""Entry point for Refund Service"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from presentation.main import app

if __name__ == "__main__":
    uvicorn.run(
        "presentation.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )