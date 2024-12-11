import paho.mqtt.client as mqtt  # Import the MQTT client library for Python
import time  # Import the time module for adding delays

# Define broker address and topic
BROKER = "localhost"  # The MQTT broker address (localhost for local testing)
TOPIC = "test/topic"  # Topic to publish messages to

def main():
    # Create a new MQTT client instance
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "python_publisher")
    # Connect the client to the broker
    client.connect(BROKER, 1883, 60)  # Default MQTT port is 1883, timeout is 60 seconds

    i = 0  # Initialize a counter variable
    while True: # Run an infinite loop
        message = f"Message {i} from Python Publisher"
        client.publish(TOPIC, message)  # Publish the message to the defined topic
        print(f"Published: {message}")
        time.sleep(1)  # Wait 1 second before sending the next message
        i += 1  # Increment the counter variable
    
    client.disconnect()  # Disconnect the client

if __name__ == "__main__":
    main()  # Call the main function
