from google.cloud import pubsub_v1
import csv
import time

# Initialize Pub/Sub client
publisher = pubsub_v1.PublisherClient()
topic_path = "projects/evident-hexagon-437915-p3/topics/OPPE_Trial_1_Train_Schedule"

# Stream data from CSV to Pub/Sub
with open("sample_train_schedule.csv", "r") as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        message = str(row).encode("utf-8")
        publisher.publish(topic_path, message)
        time.sleep(1)  # Simulates real-time data
print("Data published to Pub/Sub.")
