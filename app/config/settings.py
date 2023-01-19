from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    
    app_name: str = Field("Puan Server DB", env="APP_NAME")
    app_serve: str = Field("localhost:8000", env="APP_SERVE")
    
    branch_default_name: str = Field("main", env="BRANCH_DEFAULT_NAME")
    ignore_proposition_validation: bool = Field(True, env="IGNORE_PROPOSITION_VALIDATION")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"