import argparse
import asyncio
import logging
import sys

from api_app import settings
from clients.db_client import DBClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manage_db")

async def main():
    parser = argparse.ArgumentParser(description="Database management script")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: clear
    subparsers.add_parser("clear", help="Clear all data from the database")

    # Command: create (optional, good for checking create_all)
    # The user asked for create_all methods, effectively used for tests,
    # but having it accessible here doesn't hurt.
    subparsers.add_parser("create", help="Create all tables (if not existing)")

    args = parser.parse_args()

    client = DBClient(settings.DB_URL)

    try:
        if args.command == "clear":
            logger.info("Clearing database...")
            await client.clear_db()
        elif args.command == "create":
            logger.info("Creating tables...")
            await client.create_all()
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error executing {args.command}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
