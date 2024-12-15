### **How to Write PySpark Streaming Code: A Step-by-Step Guide**

Streaming large-scale data from Kafka and processing it with PySpark is a powerful approach for real-time data analytics. In this blog, we’ll break down the process of writing PySpark code using a practical example of streaming train schedules from Kafka and processing the messages.

---

### **Understanding the Code Structure**

Before diving into the code, let’s understand the workflow:
1. **Initialize a Spark Session**: Set up the Spark environment and load the necessary Kafka connectors.
2. **Define a Schema**: Specify the structure of the incoming JSON data.
3. **Connect to Kafka**: Read messages from a Kafka topic.
4. **Process the Data**: Parse and transform the data to a structured format.
5. **Perform Analytics**: Apply transformations or aggregations on the streaming data.
6. **Output Results**: Write the processed data to a sink, such as the console or another system.

Now let’s dive into each step, using the provided code as an example.

---

### **Step 1: Initializing the Spark Session**

A Spark session is the entry point to using Spark. It’s where you configure your application and load dependencies.

```python
from pyspark.sql import SparkSession

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("TrainScheduleStreaming") \
    .config("spark.jars.packages", 
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
    .getOrCreate()
```

- **`appName`**: Identifies your Spark application.
- **`config`**: Adds the Kafka package required to connect Spark with Kafka. Ensure the version matches your Kafka and Spark setup.

---

### **Step 2: Defining the Data Schema**

To handle structured data, PySpark requires a schema. A schema defines the column names and data types of the incoming JSON messages.

```python
from pyspark.sql.types import StructType, StringType

# Define the schema for your train data
schema = StructType() \
    .add("train_name", StringType()) \
    .add("station", StringType()) \
    .add("arrival_time", StringType()) \
    .add("departure_time", StringType()) \
    .add("sequence", StringType())
```

- **StructType**: Defines a structure for the JSON data.
- **Column Types**: Use `StringType` here because Kafka messages are received as strings.

---

### **Step 3: Reading from Kafka**

To consume messages, use the `readStream` method with Kafka-specific configurations.

```python
# Read from Kafka topic 'train-schedule-topic'
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "10.128.0.6:9092") \
    .option("subscribe", "train-schedule-topic") \
    .option("startingOffsets", "earliest") \
    .load()
```

- **`kafka.bootstrap.servers`**: IP and port of the Kafka broker.
- **`subscribe`**: Kafka topic name to consume messages from.
- **`startingOffsets`**: Specifies whether to read messages from the beginning (`earliest`) or the latest messages (`latest`).

---

### **Step 4: Parsing and Transforming Data**

Transform the Kafka messages (usually raw JSON strings) into structured data using PySpark functions.

```python
from pyspark.sql.functions import from_json, col, to_timestamp

# Parse the Kafka message value (JSON) into structured data
train_data = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Convert arrival_time and departure_time to TimestampType
train_data = train_data \
    .withColumn("arrival_time", to_timestamp(col("arrival_time"), "yyyy-MM-dd HH:mm:ss")) \
    .withColumn("departure_time", to_timestamp(col("departure_time"), "yyyy-MM-dd HH:mm:ss"))
```

- **`from_json`**: Converts JSON strings to a structured format based on the defined schema.
- **`withColumn`**: Transforms columns, here converting strings to timestamps.

---

### **Step 5: Performing Analytics**

In this example, we compute a rolling count of trains arriving at each station in 20-minute intervals.

```python
from pyspark.sql.functions import window, count

# Compute 20-minute rolling count for each station based on arrival_time
rolling_counts = train_data \
    .withWatermark("arrival_time", "20 minutes") \
    .groupBy(
        window(col("arrival_time"), "20 minutes", "5 minutes"),
        col("station")
    ) \
    .agg(count("*").alias("train_count"))
```

- **`withWatermark`**: Handles late data by specifying a maximum delay.
- **`window`**: Groups data into time intervals (20 minutes with 5-minute slides).
- **`agg`**: Performs an aggregation, here counting rows.

---

### **Step 6: Writing the Output**

Finally, write the processed data to the console for debugging or testing.

```python
# Write the output to the console in Complete mode
query = rolling_counts.writeStream \
    .outputMode("complete") \
    .format("console") \
    .trigger(processingTime="60 seconds") \
    .start()

query.awaitTermination()
```

- **`outputMode`**: In `complete` mode, writes all aggregated results to the output sink.
- **`format`**: Specifies the output format, here the console.
- **`trigger`**: Sets the processing interval.

---

### **How to Replicate for Other Use Cases**

You can adapt this code for different streaming scenarios. For example:
1. **Change the Kafka Topic**: Modify the `subscribe` option in the Kafka configuration.
2. **Update the Schema**: Adjust the schema to match the structure of your Kafka messages.
3. **Perform Different Analytics**: Replace the `groupBy` and `agg` functions to apply different transformations (e.g., averages, sums).

---

### **Testing: Dumping Messages to the Terminal**

If you want to keep things simple and just dump Kafka messages to the terminal, use this minimal modification:

```python
# Parse the Kafka message value
raw_data = df.select(col("value").cast("string"))

# Write the raw messages to the console
query = raw_data.writeStream \
    .outputMode("append") \
    .format("console") \
    .trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()
```

This setup will print all incoming messages from Kafka in their raw format, making it useful for debugging or quick testing.

---

### **Conclusion**

In this guide, you learned how to write a PySpark streaming application to consume messages from Kafka and process them in real time. The example covered initializing Spark, parsing Kafka messages, and performing rolling aggregations. With this knowledge, you can extend PySpark to a variety of streaming analytics use cases.

---

**References**:  
- [Apache Spark Streaming Documentation](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)  
- [Kafka Python Client](https://kafka-python.readthedocs.io/en/master/)  

