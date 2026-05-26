import asyncio

from app.database.seeders.oil_seeder import seed_oil
from app.database.seeders.user_seeder import seed_users


async def run_all_seeders() -> None:
    await seed_users()
    await seed_oil()
    print("All seeders completed.")


def main() -> None:
    asyncio.run(run_all_seeders())


if __name__ == "__main__":
    main()
