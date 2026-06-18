from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
import asyncpg, os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@database:5432/fastapi_database_benchmarking"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=5,
        max_size=20
    )
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

async def get_db(request: Request):
    async with request.app.state.pool.acquire() as connection:
        yield connection

@app.get(path="/greeting")
async def greetings():
    return {"message": "Hello World!"}

@app.get(path="/request")
async def requests(db=Depends(get_db)):
    rows = await db.fetch("SELECT name, description, age FROM requests;")

    return [
        {
            "name": row["name"],
            "description": row["description"],
            "age": row["age"]
        }
        for row in rows
    ]