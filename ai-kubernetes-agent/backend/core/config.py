from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # These will be populated automatically by docker-compose from your .env file
    COPILOT_GITHUB_TOKEN: str = ""
    KUBECONFIG_PATH: str = "~/.kube/config"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()