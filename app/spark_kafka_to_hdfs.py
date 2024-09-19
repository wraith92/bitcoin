from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaStreamApp") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

# Read stream from Kafka topic
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "bitcoin_prices") \
    .load()

# Convert Kafka message value to string
df = df.selectExpr("CAST(value AS STRING)")

# Write the stream to HDFS
query = df.writeStream \
    .outputMode("append") \
    .format("json") \
    .option("path", "/user/root/bitcoin_prices") \
    .option("checkpointLocation", "/user/root/checkpoint") \
    .start()

query.awaitTermination()
