from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, TimestampType
from pyspark.sql.functions import window, col, count, from_json, to_timestamp, asc

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
    .add("arrival_time", StringType()) \
    .add("departure_time", StringType()) \
    .add("sequence", StringType())  # added sequence field

# Read from Kafka topic 'train-schedule-topic'
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "10.128.0.6:9092") \
    .option("subscribe", "train-schedule-topic") \
    .option("startingOffsets", "earliest") \
    .load()

# Parse the Kafka message value (JSON) into structured data
train_data = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Convert arrival_time and departure_time to TimestampType
train_data = train_data \
    .withColumn("arrival_time", to_timestamp(col("arrival_time"), "yyyy-MM-dd HH:mm:ss")) \
    .withColumn("departure_time", to_timestamp(col("departure_time"), "yyyy-MM-dd HH:mm:ss"))

# Compute 20-minute rolling count for each station based on arrival_time
rolling_counts = train_data \
    .withWatermark("arrival_time", "20 minutes") \
    .groupBy(
        window(col("arrival_time"), "20 minutes", "5 minutes"),
        col("station")
    ) \
    .agg(count("*").alias("train_count"))

# Sort by window start (arrival_time)
rolling_counts_sorted = rolling_counts \
    .select("window", "station", "train_count") \
    .orderBy("window.start")

# Write the output to the console (for testing purposes) in Complete mode
query = rolling_counts_sorted.writeStream \
    .outputMode("complete") \
    .format("console") \
    .trigger(processingTime="60 seconds") \
    .start()

query.awaitTermination()
