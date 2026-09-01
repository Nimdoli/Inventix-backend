from dotenv import load_dotenv

# Load .env into real process environment variables using python-dotenv directly,
# bypassing pydantic-settings' own (buggy/unreliable in this setup) env_file loader.
load_dotenv()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    supabase_url: str  # used to derive the public JWKS URL for JWT verification


settings = Settings()
