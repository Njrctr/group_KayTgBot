import os
import yarl
from dotenv import load_dotenv
from dynaconf import LazySettings, Dynaconf

load_dotenv()

my_settings_files = ['settings.yaml', '.secrets.yaml']


class Configuration:
    def __init__(self):
        _settings: LazySettings = Dynaconf(settings_files=my_settings_files)
        _model = 'development' if os.environ.get("DEV", False) else 'release'

        self.configuration: LazySettings = _settings.get(_model)

    def all_configuration(self) -> LazySettings:
        self.configuration.update({
            "postgres_url": self.create_postgres_url(),
            "redis_url": self.create_redis_url(),
        })
        return self.configuration

    def create_postgres_url(self) -> str:
        data = self.configuration.get('postgres').to_dict()
        return yarl.URL.build(**data).human_repr()
    
    def create_redis_url(self) -> str:
        data = self.configuration.get('redis').to_dict()
        return yarl.URL.build(**data).human_repr()


config = Configuration().all_configuration()
