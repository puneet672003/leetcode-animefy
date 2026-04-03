import asyncio

from dotenv import load_dotenv

# loading environment variables
load_dotenv()

from core.config import Config  # noqa
from core.logger import Logger  # noqa
from core.server import Server  # noqa

if __name__ == "__main__" and Config.DEVELOPMENT:
    try:
        asyncio.run(Server.start_server())
    except KeyboardInterrupt:
        Logger.info("OK bye")
    except BaseException as e:
        Logger.error("Uncaught exception: ", exc=e)
