# Valorant Player Analysis

**API Community Link**: [Discord](https://discord.gg/XpEvmaadPA)

## How It Works

This pipeline operates in five main stages:

1. **Data Retrieval**: `main.py` calls `api.py` to fetch the latest match data from the Riot API every minute.
2. **Message Production**: `kafka_producer.py` publishes each match record to a Kafka topic, with Prometheus counters tracking success and errors.
3. **Streaming & Storage**: `spark_streaming.py` runs Spark Structured Streaming to consume from Kafka, process the data (timestamp casting, deduplication), and upsert into PostgreSQL.
4. **Dashboard**: `streamlit_app.py` loads data from PostgreSQL, calculates metrics (K/D, KDA, winrate, assist rates), and presents them in an interactive Streamlit app with filters and auto-refresh.
5. **Monitoring**: `monitoring.py` exposes Prometheus metrics (API request counts, latencies, Kafka throughput) on port 8000.

## Startup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Fix variables**
   '''bash
    Api key
    region player name #
    time zone
   '''
4. **Start services**
   ```bash
   # Zookeeper & Kafka
   zookeeper-server-start.sh config/zookeeper.properties
   kafka-server-start.sh config/server.properties
   ```

5. **Start Spark Structured Streaming**
   ```bash
   spark-submit spark_streaming.py
   ```

6. **Launch data tracker**
   ```bash
   python main.py
   ```

7. **Run dashboard**
   ```bash
   streamlit run streamlit_app.py
   ```

