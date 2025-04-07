import paho.mqtt.client as mqtt
import json
import time
import uuid

# MQTT broker configuration
BROKER = "localhost"
PORT = 1883

# Define test topics and payloads for each module (preprocessing input)
TEST_CASES = [
    {
        "topic": "task_handler/smart_home",
        "payload": {
            "method": "smart_home",
            "switch": ["switch_1"],
            "status": ["on"],
            "module_name": "preprocessing"
        },
        "description": "Test turning on switch_1 in smart home module"
    },
    {
        "topic": "task_handler/tasks_api",
        "payload": {
            "method": "todo",
            "list_all_tasks": False,
            "object_type": "task",
            "action": "insert",
            "new_task_name": "Schedule doctor appointment",
            "due_date": "2025-04-07T23:00:00",
            "module_name": "preprocessing"
        },
        "description": "Test inserting a new task in the todo module"
    },
    {
        "topic": "task_handler/general_questions",
        "payload": {
            "method": "general",
            "query": "What's the weather like on 2025-04-07?",
            "topic": "general",
            "module_name": "preprocessing"
        },
        "description": "Test querying general questions module"
    },
    {
        "topic": "task_handler/learning_resources",
        "payload": {
            "topic": "Deep Learning",
            "specific_resources": ["Courses", "Books"],
        },
        "description": "Test learning resources module with a topic and specific resources"
    }
]

# Callback function to handle responses
def on_message(client, userdata, msg):
    try:
        # Decode and parse the response
        response = json.loads(msg.payload.decode())
        print(f"Received response on topic '{msg.topic}': {json.dumps(response, indent=4)}")
    except json.JSONDecodeError:
        print(f"Received invalid JSON response on topic '{msg.topic}': {msg.payload.decode()}")

# Main function to start MQTT and process responses
def main():
    # Generate a unique client ID
    unique_client_id = f"start_mqtt_{uuid.uuid4().hex[:8]}"
    client = mqtt.Client(unique_client_id)  # Use the unique client ID
    client.on_message = on_message

    # Connect to the MQTT broker
    client.connect(BROKER, PORT, 60)

    # Subscribe to all topics to receive responses
    for case in TEST_CASES:
        client.subscribe(case["topic"])

    # Start the MQTT loop in a separate thread
    client.loop_start()

    # Publish test messages (preprocessing input)
    for case in TEST_CASES:
        print(f"Publishing to topic '{case['topic']}': {case['description']}")
        client.publish(case["topic"], json.dumps(case["payload"]))
        time.sleep(1)  # Wait for a response

    # Stop the MQTT loop and disconnect after allowing time for responses
    time.sleep(5)  # Allow time for all responses to be received
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    print("Starting MQTT and sending preprocessing input...")
    main()
