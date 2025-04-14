import paho.mqtt.client as mqtt
import json
from ast import literal_eval
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)


console_handler = logging.StreamHandler()
logger.addHandler(console_handler)


# send = {
#         'predicted_labels': ['general'],
#         'prompt': "what is the average salary for my job in my country?",
#         'module_name': 'task_classifier'
#     }
# send = {
#         'predicted_labels': ['general'],
#         'prompt': 'what about tomorrow',
#         'module_name': 'task_classifier'
#     }
# send = {
#         'predicted_labels': ['smart_home', 'todo', 'general'],
#         'prompt': 'light up the living room then schedule a doctor appointment at 11 pm and whats the weather like today',
#         'module_name': 'task_classifier'
#     }
# send = {"prompt": "Hey Bemo, light up the living room and turn of the tv and the fan"}
# send = {
#         'predicted_labels': ['others'],
#         'prompt': 'Tell me some jokes about my job',
#         'module_name': 'task_classifier'
#     }
# send = {
#         'predicted_labels': ['others'],
#         'prompt': 'Haha that was funny, tell me another one',
#         'module_name': 'task_classifier'
#     }
# send = {
#         'predicted_labels': ['learning_resources'],
#         'prompt': 'Provide me with some learning resources for my job, make sure to include some videos and books',
#         'module_name': 'task_classifier'
#     }

# send = {
#         'predicted_labels': ['learning_resources', 'todo'],
#         'prompt': 'Provide me with some learning resources about arabic language and schedule a doctor appointment at 11 pm',
#         'module_name': 'task_classifier'
#     }
send = {
        'predicted_labels': ['todo'],
        'prompt': 'Schedule a doctor appointment at 11 pm',
        'module_name': 'task_classifier'
    }
class GlobalMQTTHandler:
    """
    GlobalMQTTHandler listens on 'main/main' and publishes a list of predefined
    task payloads to 'task_handler/main' once triggered.
    """

    def __init__(self, sub_topic: str = "main/main", name: str = "global_publisher"):
        self._result = {}

        self.__pub_topic = "preprocessing/data"
        self.__sub_topic = sub_topic
        self.__name = name
        self.__qos = 1

        BROKER = "localhost"
        PORT = 1883

        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self.__name)
        except Exception:
            self.client = mqtt.Client(self.__name)

        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__callback

        self.client.connect(BROKER, PORT, 60)
        self.client.subscribe(self.__sub_topic, self.__qos)

        logger.info(f"[{self.__name}] Connected and listening to '{self.__sub_topic}'")

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"[{self.__name}] Successfully connected to broker.")
        else:
            logger.error(f"[{self.__name}] Connection failed with code {rc}.")

    def __callback(self, client, userdata, msg):
        input_data = msg.payload.decode()
        try:
            input_data_eval = literal_eval(input_data)
            logger.info(f"[{self.__name}] Received message: {input_data_eval}")
        except Exception as e:
            logger.error(f"[{self.__name}] Error processing message: {e}")

    def execute_main(self, input_data: dict | list) -> list:
        """
        Returns a predefined list of payloads to be published.
        """
        return send

    def publish_result(self, result: list):
        if result:
            payload = json.dumps(result)
            self.client.publish(self.__pub_topic, payload, self.__qos)
            logger.info(f"[{self.__name}] Published to '{self.__pub_topic}': {payload}")

    def start(self):
        self._result = self.execute_main({})
        self.publish_result(self._result)
        logger.info(f"[{self.__name}] MQTT loop started.")
        self.client.loop_forever()

if __name__ == "__main__":
    handler = GlobalMQTTHandler()
    handler.start()
