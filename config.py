# config.py
import logging

# Configure logger
logging.basicConfig(
    level=logging.INFO,  # You can set the log level to DEBUG, INFO, WARNING, etc.
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Print to console
        logging.FileHandler("app.log", mode="a")
    ]
)
logger = logging.getLogger()

POSTGRES = {
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432",
    "database": "valorant_db"
}

RIOT = {
    "api_key": "",
    "region": "",
    "name": "",
    "tag": "",
    "timezone": "",
    "match_count": 500
}

# Dynamic table name for PostgreSQL
RIOT_TABLE_NAME = f"{RIOT['name'].replace(' ', '').lower()}_{RIOT['tag'].lower()}"

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "valorant_data"
JDBC_URL = "jdbc:postgresql://localhost:5432/valorant_db"
JDBC_PROPERTIES = {"user": "postgres", "password": "1234", "driver": "org.postgresql.Driver"}
