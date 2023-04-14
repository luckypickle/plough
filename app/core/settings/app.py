import logging
import sys
from typing import Any, Dict, List, Tuple

from loguru import logger
from pydantic import PostgresDsn, SecretStr, AnyHttpUrl

from app.core.logging import InterceptHandler
from app.core.settings.base import BaseAppSettings
import datetime


from pathlib import Path

class AppSettings(BaseAppSettings):
    MCHID = ''
    PRIVATE_KEY = ''
    CERT_SERIAL_NO = ''
    APIV3_KEY = ''
    APPID = ''
    NOTIFY_URL = 'https://www.xxxx.com/notify'
    CERT_DIR = './cert'
    PARTNER_MODE = False

    FIRST_SUPERUSER = "admin@plough.com"
    FIRST_SUPERUSER_PASSWORD = "12345678"
    USERS_OPEN_REGISTRATION = True
    MASTERS_OPEN_REGISTRATION = True
    ACCESS_TOKEN_EXPIRE_MINUTES = 10
    SMS_SECRET_ID = ''
    SMS_SECRET_KEY = ''
    SMS_TEMPLATE_ID = ''
    SMS_APP_ID = ''
    SMS_SIGNATURE = ''

    SES_FROM_ADDR=''
    SES_TEMPLATE_ID=0


    EMAILS_ENABLED = True
    EMAILS_FROM_NAME = ''
    EMAILS_FROM_EMAIL = ''
    SMTP_HOST = ''
    SMTP_PORT = 25
    SMTP_TLS = False
    SMTP_USER = ''
    SMTP_PASSWORD = ''
    EMAIL_TEMPLATES_DIR = ''
    PROJECT_NAME = ''
    SERVER_HOST = ''
    EMAIL_RESET_TOKEN_EXPIRE_HOURS = 3600

    COS_SECRET_ID=""
    COS_SECRET_KEY=""
    COS_BUCKET_NAME =""
    COS_REGION = ""
    COS_REQUEST_URL=""

    IM_URL=""

    mpcode_request_interval = 60
    emailcode_request_interval = 600
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "plough"
    version: str = "0.0.0"

    database_url: PostgresDsn
    max_connection_count: int = 10
    min_connection_count: int = 10

    secret_key: SecretStr

    api_prefix: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    jwt_token_prefix: str = "Token"

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.DEBUG
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler(level=self.logging_level)]
        log_name = Path("logs", 'plough-info_'+str(datetime.date.today())+'.log')
        # 配置日志到标准输出流
        logger.configure(handlers=[{"sink": sys.stderr, "level": self.logging_level}])
        # 配置日志到输出到文件
        logger.add(log_name, rotation="500 MB", encoding='utf-8', colorize=False, level='INFO',enqueue=True)

