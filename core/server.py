import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from core.config import Config
from core.discord.bot import DiscordBot

from routes import global_router
from middlewares.auth_middleware import AuthMiddleware


class Server:
    app = None

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
        if cls.app is None:

            @asynccontextmanager
            async def lifespan(app: FastAPI):
                await DiscordBot.run_bot()
                yield
                await DiscordBot.close_conn()

            cls.app = FastAPI(lifespan=lifespan)

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
