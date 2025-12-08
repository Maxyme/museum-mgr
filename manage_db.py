import argparse
import asyncio
import logging
import sys
from sqlalchemy.ext.asyncio import create_async_engine # No longer needed here

from app import settings
from clients.db_client import DBClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manage_db")

async def main():
    parser = argparse.ArgumentParser(description="Database management script")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: clear
    subparsers.add_parser("clear", help="Clear all data from the database")

    # Command: create
    subparsers.add_parser("create", help="Create all tables (if not existing)")

    # Command: seed
    subparsers.add_parser("seed", help="Seed the database with initial data")

    args = parser.parse_args()

    # Manually create client
    client = DBClient(db_url=settings.DB_URL)
    
    try:
        if args.command == "clear":
            logger.info("Clearing database...")
            await client.clear_db()
        elif args.command == "create":
            logger.info("Creating tables...")
            await client.create_all()
        elif args.command == "seed":
            logger.info("Seeding database...")
            await client.seed_db()
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error executing {args.command}: {e}")
        sys.exit(1)
    finally:
        await client.close() # Close the client's engine

if __name__ == "__main__":
    asyncio.run(main())