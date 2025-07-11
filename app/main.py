import asyncio
from dotenv import load_dotenv

# loading environment variables
load_dotenv()

from core.config import Config
from core.logger import Logger
from core.server import Server


if __name__ == "__main__" and Config.DEVELOPMENT:
    try:
        asyncio.run(Server.start_server())
    except KeyboardInterrupt:
        Logger.info("OK bye")
    except BaseException as e:
        Logger.error("Uncaught exception: ", exc=e)
