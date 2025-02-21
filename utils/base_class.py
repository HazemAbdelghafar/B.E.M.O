import paho.mqtt.client as mqtt
import time
from ast import literal_eval


class BaseMQTTHandler:
    """
    BaseMQTTHandler is a base class for handling MQTT communication.
    """

    def __init__(self, sub_topic: str, pub_topic: str, name: str):
        """
        Initialize the BaseMQTTHandler object.

        Args:
            sub_topic (str): MQTT topic to subscribe to.
            pub_topic (str): MQTT topic to publish the result to.
            name (str): Name for the MQTT client.
        """
        
        # Define the broker address and port
        BROKER = "localhost"
        PORT = 1883
        
        self._result = {}  # Initialize the result variable
        
        # Set the input and output topics and the name of the MQTT client
        self._pub_topic = pub_topic
        self._sub_topic = sub_topic
        self._name = name
        
        # Create a new MQTT client instance
        self.client =  mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self._name)
        
        self.client.on_message = self.__callback  # Set the on_message callback function
        
        self.client.connect(BROKER, PORT, 60)  # Connect to the broker
        
        self.client.subscribe(self._sub_topic) # Subscribe to the input topic

        print(f"{self._name} initialized successfully!")
    
    def __call__(self, input_data: dict):
        """
        Executes the main functionality of the class.

        Args:
            input_data (dict): The input data to process.
        """
        start = time.time()  # Start the timer
        self._result = self._execute_main(input_data)
        end = time.time()  # End the timer
        
        print(f"Execution time: {end - start} seconds")
        
        # Publish the result after execution
        self.publish_result(self._result)
                
    def __callback(self, client: mqtt.Client, userdata: any, msg: mqtt.MQTTMessage):
        """
        Callback function for when a message is received.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata (Any): User-defined data of any type.
            msg (mqtt.MQTTMessage): The message received from the broker.
        """
        input_data = msg.payload.decode()
        input_data_dict = literal_eval(input_data)
        print(f"Received message: {input_data_dict}")
        self(input_data_dict)  # Call the main function with the received input data

    def _execute_main(self, input_data: dict) -> dict:
        """
        Executes the main function of the class.
        This method should be overridden by child classes.

        Args:
            input_data (dict): The input data to process.

        Returns:
            dict: The result of the main function.
        """
        raise NotImplementedError("This method should be overridden by child classes.")
    
    def get_result(self) -> dict:
        """
        Returns the result of the last executed main function.

        Returns:
            dict: The result of the last executed main function.
        """
        return self._result
    
    def publish_result(self, result: dict):
        """
        Publishes the result to the specified MQTT topic.

        Args:
            result (dict): The result to publish.
        """
        if result is not {}:
            result["module_name"] = self._name
            str_result = str(result)
            self.client.publish(self._pub_topic, str_result)
            print(f"Published result to topic '{self._pub_topic}': {str_result}")
