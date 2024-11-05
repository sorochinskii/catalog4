import pickle
import sys
from dataclasses import asdict, dataclass
from os import getenv

from dotenv import find_dotenv
from dump_env.dumper import dump
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    def __init__(self, env_file):
        super().__init__(_env_file=env_file, _case_sensitive=True, )

    HOST: str = Field(default='HOST')
    SSH_PRIVATE_KEY: str = Field(default='SSH_KEY')
    SSH_PASSPHRASE: str = Field(default='SSH_PASSPHRASE')
    SSH_PORT: str = Field(default='SSH_PORT')
    PROJECT_NAME: str = Field(default='PROJECT_NAME')
    ENVIRONMENT: str = Field(default='ENVIRONMENT')
    LOG_DIR: str = Field(default='LOG_DIR')
    V1: str = Field(default='V1')
    HTTP_SECURED: str = Field(default='HTTP_SECURED')
    HTTP_PORT: int | None = Field(default=None)

    # @model_validator(mode='after')
    # def set_environment(self):
    #     env_vars = EnvironmentVars()
    #     assert self.ENVIRONMENT in asdict(env_vars).values(), \
    #         f'{self.ENVIRONMENT=} not in possible {asdict(env_vars).values()}'
    #     return self

    class Config:
        validate_assignment = True


envs = find_dotenv('.env', raise_error_if_not_found=True)
settings = Settings(env_file=envs)
