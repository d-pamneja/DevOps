from pyspark.sql import SparkSession
from pyspark.sql.functions import window, col, from_json
from pyspark.sql.types import StructType, StringType, TimestampType

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("TrainScheduleStreaming") \
    .getOrCreate()

# Define schema for the train data
schema = StructType() \
    .add("station", StringType()) \
    .add("arrival_time", TimestampType()) \
    .add("departure_time", TimestampType()) \
    .add("train_name", StringType()) \
    .add("sequence", StringType())

# Read data from Pub/Sub
train_data = spark.readStream \
    .format("pubsub") \
    .option("subscription", "projects/evident-hexagon-437915-p3/subscriptions/OPPE_Trial_1_Train_Schedule-sub") \
    .load()

# Parse and transform data
train_df = train_data.selectExpr("CAST(data AS STRING)") \
    .select(from_json(col("data"), schema).alias("data")) \
    .select("data.*")

# Compute 20-minute rolling count
rolling_window = train_df \
    .withColumn("event_time", col("arrival_time")) \
    .groupBy(
        col("station"),
        window(col("event_time"), "20 minutes", "5 minutes")
    ).count()

# Output to Cloud Storage
query = rolling_window.writeStream \
    .format("json") \
    .option("path", "gs://oppe_trial_train_schedule/rolling_counts/") \
    .option("checkpointLocation", "gs://oppe_trial_train_schedule/checkpoints/") \
    .start()

query.awaitTermination()
