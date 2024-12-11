# MQTT Overview and Implementation

## What is MQTT?

MQTT (Message Queuing Telemetry Transport) is a lightweight, publish-subscribe messaging protocol designed for high-latency or unreliable networks. It is commonly used in IoT systems, robotics, and low-resource environments.

## Key Features of MQTT

1. **Broker-Based Communication**: Centralized message routing via topics.
2. **Quality of Service (QoS)**: Configurable delivery guarantees (QoS 0, 1, 2).
3. **Lightweight Protocol**: Minimal overhead, making it ideal for constrained environments.
4. **Retained Messages and Last Will**: For state persistence and handling client disconnections.

## Core Working Principle of MQTT

At its core, MQTT operates on a **publish-subscribe** mechanism:

-   A **broker** acts as the central hub for managing messages between clients.
-   Clients **publish** messages to specific topics.
-   Other clients **subscribe** to these topics to receive messages.

MQTT uses a lightweight TCP/IP protocol for transport and features keep-alive mechanisms for maintaining persistent connections, which is critical for IoT devices with intermittent connectivity.

---

## Installing Required Libraries

### Mosquitto MQTT Broker

1. Install the **Mosquitto MQTT Broker**:

    - For Ubuntu/Debian:

        ```bash
        sudo apt update
        sudo apt install mosquitto mosquitto-clients
        ```

    - For Windows/Mac, download the installer from the [Mosquitto website](https://mosquitto.org/download/).

2. Start the Mosquitto broker:

    ```bash
    sudo systemctl start mosquitto
    ```

### Python

Install the **Paho MQTT client library** using pip:

```bash
pip install paho-mqtt
```

### C++

1. Install the **Eclipse Paho MQTT C++ Library**:

    ```bash
    sudo apt-get install libpaho-mqttpp3-dev
    ```

2. Alternatively, build the library from source by following instructions on the [Paho MQTT GitHub](https://github.com/eclipse/paho.mqtt.cpp).

---

### Python Publisher Code

```python
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
```

### Python Subscriber Code

```python
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
```

### C++ Subscriber Code

```cpp
#include <iostream>                 // For standard input/output
#include <mqtt/async_client.h>      // Include the MQTT asynchronous client library

// Define constants for the MQTT broker and topic
const std::string SERVER_ADDRESS("tcp://localhost:1883");  // Broker address
const std::string CLIENT_ID("CppSubscriber");              // Unique client ID
const std::string TOPIC("test/topic");                     // Topic to subscribe to

// Define a callback class to handle incoming messages
class callback : public virtual mqtt::callback {
public:
    // This function is called when a message arrives
    void message_arrived(mqtt::const_message_ptr msg) override {
        std::cout << "Message received: " << msg->to_string() << std::endl;
    }
};

int main() {
    // Create an MQTT client instance
    mqtt::async_client client(SERVER_ADDRESS, CLIENT_ID);

    // Set up the callback to handle incoming messages
    callback cb;
    client.set_callback(cb);

    // Connect to the MQTT broker
    client.connect()->wait();

    // Subscribe to the defined topic
    client.subscribe(TOPIC, 1)->wait();  // QoS level 1 (at-least-once delivery)

    std::cout << "Listening for messages on topic: " << TOPIC << std::endl;

    // Keep the client running to listen for messages
    while (true) {
        // Infinite loop to keep the subscriber active
    }

    // Disconnect the client (not reachable in this example)
    client.disconnect()->wait();
    return 0;
}
```

Compile using: `g++ -o subscriber subscriber.cpp -lpaho-mqttpp3 -lpaho-mqtt3as`

### C++ Publisher Code

```cpp
#include <iostream>                 // For standard input/output
#include <mqtt/async_client.h>      // Include the MQTT asynchronous client library

// Define constants for the MQTT broker and topic
const std::string SERVER_ADDRESS("tcp://localhost:1883");  // Broker address
const std::string CLIENT_ID("CppPublisher");              // Unique client ID
const std::string TOPIC("test/topic");                     // Topic to publish messages to

int main() {
    // Create an MQTT client instance
    mqtt::async_client client(SERVER_ADDRESS, CLIENT_ID);

    // Connect to the MQTT broker
    client.connect()->wait();

    for (int i = 0; i < 5; ++i) {  // Publish 5 messages
        // Create a message to publish
        auto msg = mqtt::make_message(TOPIC, "Message " + std::to_string(i) + " from C++ Publisher");
        client.publish(msg)->wait();  // Publish the message and wait for acknowledgment
        std::cout << "Published: " << msg->to_string() << std::endl;
    }

    // Disconnect the client
    client.disconnect()->wait();
    return 0;
}
```

Compile using: `g++ -o publisher publisher.cpp -lpaho-mqttpp3 -lpaho-mqtt3as`

---

## Conclusion

In this report, we explored MQTT's lightweight and efficient publish-subscribe architecture, ideal for IoT and real-time systems. We detailed its core functionalities, including broker-based communication, Quality of Service (QoS) levels, and its advantages over traditional disk I/O methods. The installation guide provided an easy setup for the Mosquitto broker, along with necessary libraries for Python and C++ implementations.

With practical examples demonstrating cross-language integration between Python and C++, the flexibility and simplicity of MQTT were showcased. These examples highlight MQTT's utility in multi-language systems, enabling seamless communication between devices and applications. MQTT's low overhead, robust message delivery, and compatibility make it an indispensable tool in modern distributed systems.
