from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class AppConfig:
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_sender_name: str
    deployment_url: str
    mongo_uri: str
    mongo_db_name: str
    frontend_url: str

    @staticmethod
    def from_env() -> "AppConfig":
        return AppConfig(
            smtp_host=os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io"),
            smtp_port=int(os.getenv("SMTP_PORT", "2525")),
            smtp_username=os.getenv("SMTP_USERNAME", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            smtp_sender_name=os.getenv("SMTP_SENDER", "no-reply@example.com"),
            deployment_url=os.getenv("DEPLOYMENT_URL", "http://localhost:8000"),
            mongo_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017"),
            mongo_db_name=os.getenv("MONGO_DB_NAME", "auth_example"),
            frontend_url=os.getenv("FRONTEND_URL", "http://localhost:3000/app"),
        )


CONFIG = AppConfig.from_env()
