from celery import Celery
from utils.load_env import settings

app = Celery(
    "ai_crypto_trading_bot",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=["workers.tasks"],
)

app.conf.beat_schedule = {
    "update-coin-prices-every-hour": {
        "task": "workers.tasks.update_coin_prices_task",
        "schedule": 3600.0,
    },
}

if __name__ == "__main__":
    app.start()
