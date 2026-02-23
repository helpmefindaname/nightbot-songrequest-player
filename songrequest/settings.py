from pydantic_settings import BaseSettings, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    nightbot_client_id: str
    nightbot_client_secret: str

    model_config = SettingsConfigDict(env_file=".env")