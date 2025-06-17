import torch
import base64
import requests
import io
from kafka import KafkaConsumer
from PIL import Image
from model import model
from utils import preprocess

def process_image(image_bytes):
    image_tensor = preprocess(image_bytes)
    with torch.no_grad():
        prediction = model([image_tensor])[0]

    data = {
        "boxes": prediction["boxes"].tolist(),
        "labels": prediction["labels"].tolist(),
        "scores": prediction["scores"].tolist(),
        "image": base64.b64encode(image_bytes).decode("utf-8")
    }

    # Send to Flask server for drawing and S3 upload
    response = requests.post("http://13.50.65.62:5555/draw", json=data)
    print("Uploaded to S3:", response.json()["s3_url"])

def consume_kafka():
    consumer = KafkaConsumer(
        "images",
        bootstrap_servers="kafka:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="detector-group"
    )

    print("🚀 Kafka consumer started, waiting for messages...")
    for message in consumer:
        try:
            image_bytes = base64.b64decode(message.value)
            process_image(image_bytes)
        except Exception as e:
            print("❌ Failed to process message:", e)

if __name__ == "__main__":
    consume_kafka()
