import paho.mqtt.client as mqtt  # Import the MQTT client library for Python
import json  # Import json to handle message formatting
import time  # For optional sleep after publishing

class MQTTClientHandler:
    def __init__(self, broker="localhost", port=1883, sub_topic="server/main", client_id="server"):
        self.broker = broker
        self.port = port
        self.sub_topic = sub_topic
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)

        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port, 60)
        self.client.subscribe(self.sub_topic, qos=1)
        self.client.loop_start()
        print(f"Connected to {self.broker} and subscribed to {self.sub_topic}")

    def on_message(self, client, userdata, message):
        """
        Callback function to handle messages received from the broker.
        """
        print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

    def publish(self, topic, payload):
        """
        Publish a JSON-formatted payload to the given topic.
        """
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload)
        self.client.publish(topic, payload)
        print(f"Message published to topic {topic}")

    def stop(self):
        """
        Gracefully stop the MQTT loop and disconnect.
        """
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from broker")

# ------------------------
# Example usage
# ------------------------

if __name__ == "__main__":
    TOPIC = "task_handler/global"
    payloads = [
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
        },
        {
            "topic": "Deep Learning",
            "specific_resources": ["Courses", "Books"]
        }
    ]

    mqtt_handler = MQTTClientHandler()
    mqtt_handler.publish(TOPIC, payloads)
