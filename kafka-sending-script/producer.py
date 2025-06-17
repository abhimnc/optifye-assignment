import cv2
import time
import json
import logging
from kafka import KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RTSP_URL = "rtsp://13.50.65.62:8554/demo"
KAFKA_BROKER = "localhost:9092"
TOPIC = "demo-video-stream"

# Set up Kafka producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    linger_ms=10,
    max_request_size=5*1024*1024  # Optional: increase if needed
)

# Open RTSP stream
cap = cv2.VideoCapture(RTSP_URL)
if not cap.isOpened():
    # Use logging.error for critical failures
    logging.error(f"Failed to connect to RTSP stream: {RTSP_URL}")
    raise Exception(f"Failed to connect to RTSP stream: {RTSP_URL}")

batch = []
frame_count = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            logging.info("Failed to grab frame")
            break

        # Encode frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = buffer.tobytes()

        batch.append(frame_data)
        frame_count += 1

        if len(batch) == 25:
            # Convert frames to hex and send to Kafka
            payload = {"frames": [f.hex() for f in batch]}
            producer.send(TOPIC, value=payload)
            logging.info(f"Sent batch of 25 frames (frame {frame_count})")
            batch = []

        time.sleep(0.04)  # ~25 FPS

except KeyboardInterrupt:
    logging.info("Stopped by user")

finally:
    cap.release()
    producer.flush()
    producer.close()
