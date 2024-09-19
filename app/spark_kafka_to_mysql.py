from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, when, unix_timestamp
from pyspark.sql.types import StructType, StructField, FloatType, LongType

# Define schema for Bitcoin data
schema = StructType([
    StructField("timestamp", LongType(), True),
    StructField("buy_price", FloatType(), True),
    StructField("sell_price", FloatType(), True),
    StructField("volume", FloatType(), True)
])

# Create a Spark session
spark = SparkSession.builder \
    .appName("KafkaToMySQL") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2,mysql:mysql-connector-java:8.0.26") \
    .getOrCreate()

# Read data from Kafka topic 'bitcoin_prices'
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "bitcoin_prices") \
    .load()

# Convert Kafka data from bytes to JSON and parse according to schema
bitcoin_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Ensure timestamp is in seconds and cast to LongType
bitcoin_df = bitcoin_df.withColumn(
    "timestamp",
    (col("timestamp") / 1000).cast(LongType())
)

# Function to write to MySQL
def write_to_mysql(df, epoch_id):
    df.write \
        .format("jdbc") \
        .mode("append") \
        .option("url", "jdbc:mysql://mysql:3306/bitcoin_data") \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .option("dbtable", "bitcoin_prices") \
        .option("user", "user") \
        .option("password", "password") \
        .save()

# Write the streaming data to MySQL
bitcoin_df.writeStream \
    .foreachBatch(write_to_mysql) \
    .outputMode("append") \
    .start() \
    .awaitTermination()
