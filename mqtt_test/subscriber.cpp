#include <iostream>            // For standard input/output
#include <mqtt/async_client.h> // Include the MQTT asynchronous client library

// Define constants for the MQTT broker and topic
const std::string SERVER_ADDRESS("tcp://localhost:1883"); // Broker address
const std::string CLIENT_ID("cpp_subscriber");            // Unique client ID
const std::string TOPIC("test/topic");                    // Topic to subscribe to

// Define a callback class to handle incoming messages
class callback : public virtual mqtt::callback
{
public:
    // This function is called when a message arrives
    void message_arrived(mqtt::const_message_ptr msg) override
    {
        std::cout << "Message received: " << msg->to_string() << std::endl;
    }
};

int main()
{
    // Create an MQTT client instance
    mqtt::async_client client(SERVER_ADDRESS, CLIENT_ID);

    // Set up the callback to handle incoming messages
    callback cb;
    client.set_callback(cb);

    // Connect to the MQTT broker
    client.connect()->wait();

    // Subscribe to the defined topic
    client.subscribe(TOPIC, 1)->wait(); // QoS level 1 (at-least-once delivery)

    std::cout << "Listening for messages on topic: " << TOPIC << std::endl;

    // Keep the client running to listen for messages
    while (true)
    {
        // Infinite loop to keep the subscriber active
    }

    // Disconnect the client (not reachable in this example)
    client.disconnect()->wait();
    return 0;
}
