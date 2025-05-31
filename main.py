from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Controllers import RecipeController
from Core.db import Base, engine
from Core.redis_client import init_redis, close_redis
from contextlib import asynccontextmanager
from Core.kafka_producer import kafka_producer
from Core.kafka_consumer import kafka_consumer, handle_kafka_response

@asynccontextmanager
async def lifespan(app: FastAPI):
    await kafka_producer.start()
    await init_redis()
    await kafka_consumer.start(handle_kafka_response)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await close_redis()
    await kafka_consumer.stop()
    await kafka_producer.stop()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(RecipeController.router, prefix="/api/v1", tags=["Recipes"])