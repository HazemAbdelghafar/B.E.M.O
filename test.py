import paho.mqtt.client as mqtt  # Import the MQTT client library for Python

# Define broker address and topic
BROKER = "localhost"  # The MQTT broker address (localhost for local testing)
# TOPIC = "task_classifier/prompt"
TOPIC = "preprocessing/prompt"

# Create a new MQTT client instance
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "python_publisher")
# Connect the client to the broker
client.connect(BROKER, 1883, 60)  # Default MQTT port is 1883, timeout is 60 seconds

send = {
        'predicted_labels': ['smart_home', 'todo', 'general'],
        'preprocessed_prompt': 'light up the living room then schedule a doctor appointment at 11 pm and whats the weather like tomorrow',
        'module_name': 'task_classifier'
    }
# send = {"prompt": "Hey Bemo, light up the living room then schedule a doctor appointment at 11 pm and whats the weather like tomorrow"}

client.publish(TOPIC, str(send))  # Publish the message to the defined topic
print(f"Message published to topic {TOPIC}")

client.disconnect()  # Disconnect the client
print("Disconnected from the broker")
