import asyncio
from core.telegram import start_bot, stop_bot
from core.backend.database import create_all_tables
from core.schedule import schedule


async def main():
    try:
        await create_all_tables()
        schedule.start_scheduler()
        await start_bot()
    except (KeyboardInterrupt, SystemExit):
        await stop_bot()
    finally:
        loop.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
