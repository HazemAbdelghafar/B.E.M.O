import paho.mqtt.client as mqtt  # Import the MQTT client library for Python

# Define broker address and topic
BROKER = "localhost"  # The MQTT broker address (localhost for local testing)
TOPIC = "test/topic"  # Topic to subscribe to

# Callback function for when a message is received
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()}")  # Print the received message

def main():
    # Create a new MQTT client instance
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "python_subscriber")
    # Assign the callback function for handling messages
    client.on_message = on_message

    # Connect the client to the broker
    client.connect(BROKER, 1883, 60)  # Default MQTT port is 1883, timeout is 60 seconds

    # Subscribe to the defined topic
    client.subscribe(TOPIC)

    # Start the loop to process incoming messages
    client.loop_forever()

if __name__ == "__main__":
    main()  # Call the main function
