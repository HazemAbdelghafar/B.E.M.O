import paho.mqtt.client as mqtt
import time
from ast import literal_eval
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)


console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

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

        logger.info(f"{self.__name} initialized successfully!")
    
    def __built_in_run(self, input_data: dict | list):
        """
        Executes the main functionality of the class.

        Args:
            input_data (dict | list): The input data to process.
        """
        start = time.time()  # Start the timer
        try:
            self._result = self.execute_main(input_data)
        except Exception as e:
            logger.error(f"Error in executing main function: {e}")
            self._result = {"error": str(e)}
        end = time.time()  # End the timer
        
        logger.info(f"Execution time for {self.__name}: {end - start} seconds")
        
        # Publish the result after execution
        if self._result:
            self.publish_result(self._result)
        
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
            logger.info("Connected to broker!")
        else:
            logger.error(f"Failed to connect, return code {rc}")
            
            is_connected = False
            
            while not is_connected:
                # Try to reconnect if the connection fails
                try:
                    self.client.reconnect()
                    logger.info("Reconnecting to broker...")
                except Exception as e:
                    logger.error(f"Reconnection failed: {e}")
                    time.sleep(5)
                else:
                    is_connected = True
                    logger.info("Reconnected to broker!")
                    self.client.subscribe(self.__sub_topic, self.__qos)  # Resubscribe to the topic
                    logger.info(f"Subscribed to topic '{self.__sub_topic}'")
    
    def __callback(self, client: mqtt.Client, userdata: any, msg: mqtt.MQTTMessage):
        """
        Callback function for when a message is received.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata (Any): User-defined data of any type.
            msg (mqtt.MQTTMessage): The message received from the broker.
        """
        try:
            input_data = msg.payload.decode()
        except Exception as e:
            logger.error(f"Error decoding message: {e}")
            return
        try:
            input_data_parsed = literal_eval(input_data)
        except:
            input_data_parsed = json.loads(input_data)
            
        logger.info(f"Received message: {input_data_parsed}")
        self.__built_in_run(input_data_parsed)  # Call the main function with the received input data

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
    
    def publish_result(self, result: dict | list, topic: str = None):
        """
        Publishes the result to the specified MQTT topic.

        Args:
            result (dict | list): The result to publish.
        """
        if not topic:
            topic = self.__pub_topic

        if result is not {}:
            result["module_name"] = self.__name
            str_result = str(result)
            try:
                self.client.publish(topic, str_result, self.__qos)
            except Exception as e:
                logger.error(f"Error publishing result: {e}")
                return
            
            logger.info(f"Published result to topic '{topic}': {str_result}")
    
    def start(self):
        """
        Starts the MQTT client loop.
        """
        self.client.loop_forever()