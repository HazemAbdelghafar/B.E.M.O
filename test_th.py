import paho.mqtt.client as mqtt
import json
from ast import literal_eval


class GlobalMQTTHandler:
    """
    GlobalMQTTHandler listens on 'server/main' and publishes a list of predefined
    task payloads to 'task_handler/global' once triggered.
    """

    def __init__(self, sub_topic: str = "server/main", name: str = "global_publisher"):
        self._result = {}

        self.__pub_topic = "task_handler/global"
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

        print(f"[{self.__name}] Connected and listening to '{self.__sub_topic}'")

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{self.__name}] Successfully connected to broker.")
        else:
            print(f"[{self.__name}] Connection failed with code {rc}.")

    def __callback(self, client, userdata, msg):
        input_data = msg.payload.decode()
        try:
            input_data_eval = literal_eval(input_data)
            print(f"[{self.__name}] Received message: {input_data_eval}")
        except Exception as e:
            print(f"[{self.__name}] Error processing message: {e}")

    def execute_main(self, input_data: dict | list) -> list:
        """
        Returns a predefined list of payloads to be published.
        """
        return [
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
                "method": "learning_resources",
                "topic": "Deep Learning",
                "specific_resources": ["Courses", "Books"],
                "module_name": "preprocessing"
            }
        ]

    def publish_result(self, result: list):
        if result:
            payload = json.dumps(result)
            self.client.publish(self.__pub_topic, payload, self.__qos)
            print(f"[{self.__name}] Published to '{self.__pub_topic}': {payload}")

    def start(self):
        self._result = self.execute_main({})
        self.publish_result(self._result)
        print(f"[{self.__name}] MQTT loop started.")
        self.client.loop_forever()

if __name__ == "__main__":
    handler = GlobalMQTTHandler()
    handler.start()
