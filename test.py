import asyncio
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

import json
from models.auth import SessionData
from managers.session_data import SessionManager


async def main():
    session_data = SessionData(
        user={"username": "puneefffffttttt"},
        token={"access_token": "testing", "ex": 100},
    )

    result = await SessionManager.delete_session(
        "1RzArkYjILgofqUUs742tOw2HtKvTPGRbCM1pyqO35g"
        # session_data
    )
    sample_redirect = "http://localhost:8000/#token_type=Bearer&access_token=MTM1MDc1NjczNTM5MjE1MzYwMQ.WdtxDUcVK3tAhlmusowJvSdrCNyaqm&expires_in=604800&scope=guilds+identify"

    pprint(result)


async def run_all():
    await asyncio.gather(main())


asyncio.run(run_all())
