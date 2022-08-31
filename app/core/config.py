from functools import lru_cache
from typing import Dict, Type

from app.core.settings.app import AppSettings
from app.core.settings.base import AppEnvTypes, BaseAppSettings
from app.core.settings.development import DevAppSettings
from app.core.settings.production import ProdAppSettings
from app.core.settings.test import TestAppSettings

environments: Dict[AppEnvTypes, Type[AppSettings]] = {
    AppEnvTypes(AppEnvTypes.dev): DevAppSettings,
    AppEnvTypes(AppEnvTypes.prod): ProdAppSettings,
    AppEnvTypes(AppEnvTypes.test): TestAppSettings,
}


@lru_cache
def get_app_settings() -> AppSettings:
    app_env: AppEnvTypes = BaseAppSettings().app_env
    print(app_env)
    config = environments[app_env]
    return config()
