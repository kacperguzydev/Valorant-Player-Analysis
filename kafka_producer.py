# kafka_producer.py
import json
import time
import logging
from kafka import KafkaProducer
import config

# Import our monitoring counters
from monitoring import KAFKA_MESSAGES_SENT, KAFKA_SEND_ERRORS

logger = logging.getLogger(__name__)

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

def key_serializer(key: str) -> bytes:
    return key.encode("utf-8")

def produce_match_data(match_data):
    try:
        producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BROKER,
            value_serializer=json_serializer,
            key_serializer=key_serializer
        )
    except Exception as exc:
        logger.error("Kafka producer initialization failed: %s", exc)
        # Count initialization failures as send errors
        KAFKA_SEND_ERRORS.inc()
        return

    if not match_data:
        logger.warning("No match data to send to Kafka.")
        return

    logger.info("Sending %d records to Kafka.", len(match_data))
    for record in match_data:
        message_key = f"{record['match_id']}_{record['winning_team']}"
        try:
            producer.send(config.KAFKA_TOPIC, key=message_key, value=record)
            # Track successful send
            KAFKA_MESSAGES_SENT.inc()
            logger.info("Sent record: %s", message_key)
        except Exception as exc:
            # Track send errors
            KAFKA_SEND_ERRORS.inc()
            logger.error("Error sending %s: %s", message_key, exc)
        time.sleep(0.1)

    try:
        producer.flush()
        logger.info("All Kafka messages flushed successfully.")
    except Exception as exc:
        KAFKA_SEND_ERRORS.inc()
        logger.error("Error flushing Kafka producer: %s", exc)
