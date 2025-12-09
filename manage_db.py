import argparse
import asyncio
import logging
import sys
import asyncpg
from pgqueuer.queries import Queries

from app import settings
from clients.db_client import DBClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manage_db")

async def install_pgqueuer_schema(db_url: str):
    # Strip +asyncpg if present
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    logger.info(f"Installing pgqueuer schema to {db_url}")
    conn = await asyncpg.connect(db_url)
    try:
        queries = Queries.from_asyncpg_connection(conn)
        await queries.install()
        logger.info("PgQueuer schema installed successfully.")
    except asyncpg.exceptions.DuplicateObjectError:
        logger.info("PgQueuer schema already exists (DuplicateObjectError). Skipping.")
    except Exception as e:
        # Check if error message indicates existence (sometimes asyncpg wraps it differently?)
        if "already exists" in str(e):
             logger.info(f"PgQueuer schema seems to exist ({e}). Skipping.")
        else:
            logger.error(f"Failed to install schema: {e}")
            raise
    finally:
        await conn.close()

async def main():
    parser = argparse.ArgumentParser(description="Database management script")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: clear
    subparsers.add_parser("clear", help="Clear all data from the database")

    # Command: create
    subparsers.add_parser("create", help="Create all tables (if not existing)")

    # Command: seed
    subparsers.add_parser("seed", help="Seed the database with initial data")

    # Command: install-queue
    subparsers.add_parser("install-queue", help="Install pgqueuer schema")

    # Command: wait
    subparsers.add_parser("wait", help="Wait for database to be ready")

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
        elif args.command == "install-queue":
             # We can't use DBClient here directly as we need asyncpg connection
             await install_pgqueuer_schema(settings.DB_URL)
        elif args.command == "wait":
            logger.info("Waiting for database...")
            await client.wait_for_db()
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
