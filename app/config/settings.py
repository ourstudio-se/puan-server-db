from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    
    app_name: str = "Similarity API"
    app_serve: str = Field("localhost:8000", env="APP_SERVE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"