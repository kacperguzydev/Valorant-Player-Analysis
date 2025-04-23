import time
from postgresql_database import create_database, create_tables
from api import get_matches
from kafka_producer import produce_match_data
from monitoring import start_metrics_server
from config import logger

def main():
    start_metrics_server(8000)
    logger.info("Metrics server started on port 8000")

    # One-time setup
    create_database()
    create_tables()

    while True:
        try:
            logger.info("Fetching match data from API…")
            data = get_matches()
            if isinstance(data, str):
                logger.warning(data)
            else:
                produce_match_data(data)
        except Exception as e:
            logger.exception("Unexpected error in polling loop:")
        finally:
            # sleep regardless of success/failure
            time.sleep(60)

if __name__ == "__main__":
    main()
