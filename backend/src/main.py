from fastapi import FastAPI, APIRouter

from src.core.database import setup_database
from src.core.middlewares import setup_middlewares
from src.core.router import v1_router

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})

main_router = APIRouter()
main_router.include_router(v1_router)


app.include_router(main_router)
setup_middlewares(app)


@app.on_event("startup")
async def startup_event():
    await setup_database()


@app.get("/")
async def root():
    return {"message": "Hello World"}