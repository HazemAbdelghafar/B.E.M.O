#include <iostream>            // For standard input/output
#include <mqtt/async_client.h> // Include the MQTT asynchronous client library

// Define constants for the MQTT broker and topic
const std::string SERVER_ADDRESS("tcp://localhost:1883"); // Broker address
const std::string CLIENT_ID("cpp_publisher");             // Unique client ID
const std::string TOPIC("test/topic");                    // Topic to publish messages to

int main()
{
    // Create an MQTT client instance
    mqtt::async_client client(SERVER_ADDRESS, CLIENT_ID);

    // Connect to the MQTT broker
    client.connect()->wait();

    int i = 0;
    while (true)
    {
        // Create a message to publish
        auto msg = mqtt::make_message(TOPIC, "Message " + std::to_string(i) + " from C++ Publisher");
        client.publish(msg)->wait(); // Publish the message and wait for acknowledgment
        std::cout << "Published: " << msg->to_string() << std::endl;
        i++;
        std::this_thread::sleep_for(std::chrono::seconds(1)); // Wait for 1 second
    }

    // Disconnect the client
    client.disconnect()->wait();
    return 0;
}