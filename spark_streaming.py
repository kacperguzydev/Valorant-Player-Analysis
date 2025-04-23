import os

import logging
import psycopg2
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField,
    StringType, IntegerType
)
import config

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger(__name__)

logger = setup_logger()

# same schema you already have
valorant_schema = StructType([
    StructField("match_id",     StringType(),  True),
    StructField("puuid",        StringType(),  True),
    StructField("map_name",     StringType(),  True),
    StructField("mode",         StringType(),  True),
    StructField("game_start",   StringType(),  True),
    StructField("winning_team", StringType(),  True),
    StructField("agent",        StringType(),  True),
    StructField("team",         StringType(),  True),
    StructField("kills",        IntegerType(), True),
    StructField("deaths",       IntegerType(), True),
    StructField("assists",      IntegerType(), True),
    StructField("score",        IntegerType(), True),
    StructField("damage",       IntegerType(), True),
    StructField("result",       StringType(),  True),
])

def write_to_postgres(batch_df: DataFrame, batch_id: int) -> None:
    # drop duplicates within this batch
    df = batch_df.dropDuplicates(["match_id"])
    records = df.collect()
    if not records:
        logger.info(f"Batch {batch_id}: no new records")
        return

    # open a psycopg2 connection
    conn = psycopg2.connect(**config.POSTGRES)
    cur  = conn.cursor()

    # ON CONFLICT upsert against match_id
    sql = f"""
    INSERT INTO {config.RIOT_TABLE_NAME} (
      match_id, puuid, map_name, mode, game_start,
      winning_team, agent, team,
      kills, deaths, assists, score, damage, result
    ) VALUES (
      %s, %s, %s, %s, %s,
      %s, %s, %s,
      %s, %s, %s, %s, %s, %s
    )
    ON CONFLICT (match_id) DO NOTHING;
    """

    for r in records:
        cur.execute(sql, (
            r.match_id, r.puuid, r.map_name, r.mode,    r.game_start,
            r.winning_team, r.agent, r.team,
            r.kills,        r.deaths, r.assists, r.score,
            r.damage,       r.result
        ))

    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"Batch {batch_id}: upserted {len(records)} records")

def main() -> None:
    spark = (
        SparkSession.builder
            .appName("ValorantUpsert")
            .config(
              "spark.jars.packages",
              "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
              "org.postgresql:postgresql:42.2.18"
            )
            .getOrCreate()
    )

    kafka_df = (
        spark.readStream.format("kafka")
             .option("kafka.bootstrap.servers", config.KAFKA_BROKER)
             .option("subscribe", config.KAFKA_TOPIC)
             .option("failOnDataLoss", "false")
             .load()
    )

    json_df = kafka_df.selectExpr("CAST(value AS STRING) AS json_str")
    matches = (
        json_df
          .select(F.from_json("json_str", valorant_schema).alias("m"))
          .select("m.*")
    )

    # cast the ISO string into a real Timestamp
    matches = matches.withColumn("game_start", F.to_timestamp("game_start"))

    query = (
        matches.writeStream
               .outputMode("append")
               .foreachBatch(write_to_postgres)
               .option("checkpointLocation", "/tmp/checkpoint_valorant")
               .start()
    )

    query.awaitTermination()

if __name__ == "__main__":
    main()
