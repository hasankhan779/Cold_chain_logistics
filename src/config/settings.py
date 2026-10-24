import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/cold_chain_db"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "cold-chain-sops"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
