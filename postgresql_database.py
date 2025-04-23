# postgresql_database.py
import psycopg2
from psycopg2 import sql
import sys
from config import POSTGRES, RIOT_TABLE_NAME, logger

def create_database():
    logger.info("Connecting to default 'postgres' database to create the target database.")
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=POSTGRES["user"],
            password=POSTGRES["password"],
            host=POSTGRES["host"],
            port=POSTGRES["port"]
        )
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (POSTGRES["database"],))
        exists = cur.fetchone()

        if not exists:
            logger.info(f"Creating database: {POSTGRES['database']}")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(POSTGRES["database"])
            ))
        else:
            logger.info(f"Database '{POSTGRES['database']}' already exists.")

        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        sys.exit(1)

def create_tables():
    logger.info(f"Creating table '{RIOT_TABLE_NAME}' in database '{POSTGRES['database']}'.")
    try:
        conn = psycopg2.connect(**POSTGRES)
        cur = conn.cursor()

        cur.execute(sql.SQL(f"""
            CREATE TABLE IF NOT EXISTS {RIOT_TABLE_NAME} (
                match_id     TEXT        PRIMARY KEY,
                puuid        TEXT,
                map_name     TEXT,
                mode         TEXT,
                game_start   TIMESTAMP,
                winning_team TEXT,
                agent        TEXT,
                team         TEXT,
                kills        INT,
                deaths       INT,
                assists      INT,
                score        INT,
                damage       INT,
                result       TEXT
            );
        """))

        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Table '{RIOT_TABLE_NAME}' created successfully.")
    except Exception as e:
        logger.error(f"Failed to create table '{RIOT_TABLE_NAME}': {e}")
        sys.exit(1)
