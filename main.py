import asyncio
from dotenv import load_dotenv

# loading environment variables
load_dotenv()

from core.logger import logger
from core.server import Server


if __name__ == "__main__":
    try:
        asyncio.run(Server.start_server())
    except KeyboardInterrupt:
        logger.info("OK bye")
    except BaseException as e:
        logger.error("Uncaught exception: ", exc=e)
