from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL
from redis import Redis

class PostgresqlSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PSQL")

    host: str
    port: int
    user: str
    password: SecretStr
    db: str

class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='REDIS')

    host: str
    port: int
    user: str
    password: SecretStr
    db: int

class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    developer_id: int
    admin_ids: list[int]
    webhooks: bool

    bot_token: SecretStr

    webhook_url: SecretStr
    webhook_secret_token: SecretStr

    psql = PostgresqlSettings()
    redis = RedisSettings()
    
    def psql_url(self) -> URL:
        return URL.create(
            drivername='postgresql+asyncpg',
            username=self.psql.user,
            password=self.psql.password.get_secret_value(),
            host=self.psql.host,
            port=self.psql.port,
            database=self.psql.db
        )
    
    def redis_dsn(self) -> Redis:
        return Redis.from_url(
            f"redis://{self.redis.user}:{self.redis.password.get_secret_value()}@{self.redis.host}:{self.redis.port}/{self.redis.db}"
        )