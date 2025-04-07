import paho.mqtt.client as mqtt
import json
import time
import uuid  # Import uuid for generating unique client IDs

# MQTT broker configuration
BROKER = "localhost"
PORT = 1883

# Define test topics and payloads for each module
TEST_CASES = [
    {
        "method": "smart_home",
        "switch": ["switch_1"],
        "status": ["on"],
        "module_name": "preprocessing"
    },
    {
        "method": "todo",
        "list_all_tasks": False,
        "object_type": "task",
        "action": "insert",
        "new_task_name": "Schedule doctor appointment",
        "due_date": "2025-04-07T23:00:00",
        "module_name": "preprocessing"
    },
    {
        "method": "general",
        "query": "What's the weather like on 2025-04-07?",
        "topic": "general",
        "module_name": "preprocessing"
    }
]

# Callback function to handle responses
def on_message(client, userdata, msg):
    print(f"Received response on topic '{msg.topic}': {msg.payload.decode()}")

# Main function to test modules
def main():
    # Generate a unique client ID
    unique_client_id = f"test_client_{uuid.uuid4().hex[:8]}"
    client = mqtt.Client(unique_client_id)  # Use the unique client ID
    client.on_message = on_message

    # Connect to the MQTT broker
    client.connect(BROKER, PORT, 60)

    # Subscribe to all topics to receive responses
    for case in TEST_CASES:
        client.subscribe(case["topic"])

    # Start the MQTT loop in a separate thread
    client.loop_start()

    # Publish test messages
    for case in TEST_CASES:
        print(f"Publishing to topic '{case['topic']}': {case['description']}")
        client.publish(case["topic"], json.dumps(case["payload"]))
        time.sleep(1)  # Wait for a response

    # Stop the MQTT loop and disconnect
    time.sleep(5)  # Allow time for all responses to be received
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
