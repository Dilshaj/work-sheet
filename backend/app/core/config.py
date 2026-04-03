from pydantic_settings import BaseSettings
from urllib.parse import quote_plus


class Settings(BaseSettings):
    PROJECT_NAME: str = "EduProva Backend"

    # Database Settings
    DB_HOST: str
    DB_PORT: str = "1433"
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://18.60.233.8",
        "http://18.60.233.8:5000"
    ]

    # JWT
    SECRET_KEY: str = "EduProva_Default_Secret_Key_Change_Me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def get_database_url(self) -> str:
        encoded_password = quote_plus(self.DB_PASSWORD)

        return (
            f"mssql+pyodbc://{self.DB_USER}:{encoded_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver=ODBC+Driver+18+for+SQL+Server"
            f"&Encrypt=yes&TrustServerCertificate=yes"
        )

    class Config:
        env_file = ".env"


settings = Settings()
