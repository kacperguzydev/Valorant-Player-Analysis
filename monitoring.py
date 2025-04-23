from prometheus_client import start_http_server, Counter, Histogram
import functools

# Metrics definitions
API_REQUESTS_TOTAL = Counter(
    'api_requests_total',
    'Total number of API requests to Riot endpoint'
)
API_REQUEST_LATENCY_SECONDS = Histogram(
    'api_request_latency_seconds',
    'Latency of API requests in seconds'
)
KAFKA_MESSAGES_SENT = Counter(
    'kafka_messages_sent_total',
    'Total number of messages successfully sent to Kafka'
)
KAFKA_SEND_ERRORS = Counter(
    'kafka_send_errors_total',
    'Total number of errors encountered when sending to Kafka'
)

# Start metrics HTTP server on /metrics

def start_metrics_server(port: int = 8000):
    """
    Launch Prometheus metrics endpoint on the given port (default 8000).
    """
    start_http_server(port)

# Decorator to measure API calls

def track_api_request(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        API_REQUESTS_TOTAL.inc()
        with API_REQUEST_LATENCY_SECONDS.time():
            return func(*args, **kwargs)
    return wrapper
