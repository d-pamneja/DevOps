from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, TimestampType
from pyspark.sql.functions import window, col, count, from_json
from pyspark.sql.functions import col

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("TrainScheduleStreaming") \
    .config("spark.jars.packages", 
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
    .getOrCreate()

# Define the schema for your train data
schema = StructType() \
    .add("train_name", StringType()) \
    .add("station", StringType()) \
    .add("arrival_time", TimestampType()) \
    .add("departure_time", TimestampType())

# Read from Kafka (you'll need to set up a Kafka bridge for Pub/Sub)
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "your-kafka-bootstrap-server") \
    .option("subscribe", "your-kafka-topic") \
    .option("startingOffsets", "latest") \
    .load()

# Parse the Kafka message value
train_data = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Compute 20-minute rolling count for each station
rolling_counts = train_data \
    .withWatermark("arrival_time", "20 minutes") \
    .groupBy(
        window(col("arrival_time"), "20 minutes", "5 minutes"),
        col("station")
    ) \
    .agg(count("*").alias("train_count"))

# Write the output to the console (for testing purposes)
query = rolling_counts.writeStream \
    .outputMode("update") \
    .format("console") \
    .start()

query.awaitTermination()