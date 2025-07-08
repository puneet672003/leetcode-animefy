import asyncio
from dotenv import load_dotenv

# loading environment variables
load_dotenv()

from core.logger import logger
from core.server import Server
from core.discord_bot import DiscordBot


async def main():
    await asyncio.gather(Server.start_server(), DiscordBot.run_bot())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("OK bye")
    except BaseException as e:
        logger.error("Uncaught exception: ", exc=e)
