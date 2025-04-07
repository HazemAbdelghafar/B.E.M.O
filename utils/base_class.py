import paho.mqtt.client as mqtt
import time
from ast import literal_eval


class BaseMQTTHandler:
    """
    BaseMQTTHandler is a base class for handling MQTT communication.
    """

    def __init__(self, sub_topic: str, name: str):
        """
        Initialize the BaseMQTTHandler object.

        Args:
            sub_topic (str): MQTT topic to subscribe to.
            name (str): Name for the MQTT client.
        """
        
        # Define the broker address and port
        BROKER = "localhost"
        PORT = 1883
        SERVER_PUB_TOPIC = "server/main"

        self._result = {}  # Initialize the result variable
        
        # Set the input and output topics and the name of the MQTT client
        self.__pub_topic = SERVER_PUB_TOPIC 
        self.__sub_topic = sub_topic
        self.__name = name
        self.__qos = 1  # Quality of Service level
        
        # Create a new MQTT client instance
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self.__name)
        except Exception as e:
            self.client =  mqtt.Client(self.__name)
        
        self.client.on_message = self.__callback  # Set the on_message callback function
        self.client.on_connect = self.__on_connect  # Set the on_connect callback function
    
        self.client.connect(BROKER, PORT, 60)  # Connect to the broker
        
        self.client.subscribe(self.__sub_topic, self.__qos) # Subscribe to the input topic

        print(f"{self.__name} initialized successfully!")
    
    def __call__(self, input_data: dict | list):
        """
        Executes the main functionality of the class.

        Args:
            input_data (dict | list): The input data to process.
        """
        start = time.time()  # Start the timer
        self._result = self.execute_main(input_data)
        end = time.time()  # End the timer
        
        print(f"Execution time for {self.__name}: {end - start} seconds")
        
        # Publish the result after execution
        if self._result:
            self.publish_result_server(self._result)
        
    def __on_connect(self, client: mqtt.Client, userdata: any, flags: dict, rc: int):
        """
        Callback function for when the client connects to the broker.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata (Any): User-defined data of any type.
            flags (dict): Response flags sent by the broker.
            rc (int): The connection result code.
        """
        if rc == 0:
            print("Connected to broker!")
        else:
            print(f"Failed to connect, return code {rc}")
    
    #! Overridden in server class only  
    def __callback(self, client: mqtt.Client, userdata: any, msg: mqtt.MQTTMessage):
        """
        Callback function for when a message is received.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata (Any): User-defined data of any type.
            msg (mqtt.MQTTMessage): The message received from the broker.
        """
        input_data = msg.payload.decode()
        input_data_eval = literal_eval(input_data)
        print(f"Received message: {input_data_eval}")
        self(input_data_eval)  # Call the main function with the received input data

    def execute_main(self, input_data: dict | list) -> dict | list:
        """
        Executes the main function of the class.
        This method should be overridden by child classes.

        Args:
            input_data (dict | list): The input data to process.

        Returns:
            dict | list: The result of the main function.
        """
        raise NotImplementedError("This method should be overridden by child classes.")
    
    def get_result(self) -> dict | list:
        """
        Returns the result of the last executed main function.

        Returns:
            dict | list: The result of the last executed main function.
        """
        return self._result
    
    def publish_result_server(self, result: dict | list):
        """
        Publishes the result to the specified MQTT topic.

        Args:
            result (dict | list): The result to publish.
        """
        if result is not {}:
            result["module_name"] = self.__name
            str_result = str(result)
            self.client.publish(self.__pub_topic, str_result, self.__qos)
            print(f"Published result to topic '{self.__pub_topic}': {str_result}")

    def publish_result_specific(self, result: dict | list, topic: str):
        """
        Publishes the result to the specified MQTT topic.

        Args:
            result (dict | list): The result to publish.
            topic (str): The topic to publish the result to.
        """
        if result is not {}:
            result["module_name"] = self.__name
            str_result = str(result)
            self.client.publish(topic, str_result, self.__qos)
            print(f"Published result to topic '{topic}': {str_result}")
    
    def start(self):
        """
        Starts the MQTT client loop.
        """
        self.client.loop_forever()