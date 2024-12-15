import csv
import time
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers="10.128.0.6:9092", value_serializer=lambda v: v.encode("utf-8"))

with open("sample_train_schedule.csv", "r") as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        message = str(row)
        producer.send("train-schedule-topic", message)
        print(f"Published: {message}")
        time.sleep(1)

print("Data published to Kafka topic.")
