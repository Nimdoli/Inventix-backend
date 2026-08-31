from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    supabase_url: str  # used to derive the public JWKS URL for JWT verification

    class Config:
        env_file = ".env"


settings = Settings()
