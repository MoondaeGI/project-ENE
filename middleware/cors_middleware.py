"""CORS 미들웨어"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

logger = logging.getLogger(__name__)


def setup_cors(app: FastAPI) -> None:
    allow_origins = settings.cors_origins
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

