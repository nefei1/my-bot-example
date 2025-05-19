from environs import Env

env = Env()
env.read_env()

BOT_TOKEN: str = env.str("BOT_TOKEN")

WEBHOOK_SERVER_HOST: str = env.str("WEBHOOK_SERVER_HOST")
WEBHOOK_SERVER_PORT: int = env.str("WEBHOOK_SERVER_PORT")
WEBHOOK_URL: str = env.str("WEBHOOK_URL")
WEBHOOK_SERVER_PATH: str = env.str("WEBHOOK_SERVER_PATH")

DB_USER: str = env.str("DB_USER")
DB_PASSWORD: str = env.str("DB_PASSWORD")
DB_HOST: str = env.str("DB_HOST")
DB_PORT: int = env.str("DB_PORT")
DB_NAME: str = env.str("DB_NAME")
DB_LINK = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"