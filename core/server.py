import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import Config
from routes import global_router

from middlewares.auth_middleware import AuthMiddleware


class Server:
    app = FastAPI()

    @classmethod
    def setup_routes(cls):
        @cls.app.get("/")
        async def root():
            return {"message": "Hello from FastAPI!"}

        cls.app.include_router(global_router)

    @classmethod
    def setup_middleware(cls):
        cls.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        cls.app.add_middleware(AuthMiddleware)

    @classmethod
    def create_app(cls):
        cls.setup_middleware()
        cls.setup_routes()
        return cls.app

    @classmethod
    async def start_server(cls):
        app = cls.create_app()
        config = uvicorn.Config(
            app=app, host=Config.SERVER_HOST, port=Config.SERVER_PORT
        )
        server = uvicorn.Server(config)

        await server.serve()
