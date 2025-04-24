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
# send = {
#         'predicted_labels': ['todo'],
#         'prompt': 'Schedule a doctor appointment at 11 pm',
#         'module_name': 'task_classifier'
# }

# send = {'results': {'result_list': [{'id': 'bXhoc21wNmI0anhyNkNqcw', 'list_id': 'MTE3NDYyMDEyNzE5NTgwODc4Njc6MDow', 'name': 'Water the plants', 'list_name': 'My Tasks', 'last_updated': '2025-04-14 18:30:51', 'due_date': '2025-04-14 02:00:00', 'completed_date': None, 'is_done': False, 'notes': '5 ml of pure water and 3 ml of mineral water', 'parent_id': None, 'last_updated_relative': '34 minutes ago, 12 seconds ago', 'completed_date_relative': None, 'due_date_relative': '17 hours ago, 10 minutes ago', 'parent_title': None}], 'module_name': 'todo'},
# 'module_name': 'task_handler', 
# 'prompt': "Hey Robot, Check my tasks for today",
# 'emotions': {'curiosity': 0.645,
#         'neutral': 0.329,
#         'confusion': 0.059
#     }
# }
# send = {'results': 
#         {'query': "What's the weather like on 2025-04-14 in Alamein, Egypt?", 'answer': 'On April 14, 2025, Alamein will have partly cloudy skies with a temperature of 17.3C (63.1F). Winds will come from the WNW at 7.6 mph (12.2 kph). No precipitation is expected.', 'topic': 'general', 'module_name': 'general'},
# 'module_name': 'task_handler', 
# 'prompt': "Hey Robot, Check my tasks for today",
# 'emotions': {'curiosity': 0.645,
#         'neutral': 0.329,
#         'confusion': 0.059
#     }
# }
# send = {'results': 
#         {'statuses': [{'switch': 'switch_2', 'status': 'on', 'success': True}], 'module_name': 'smart_home'},
# 'module_name': 'task_handler', 
# 'prompt': "Hey Robot, Turn the fan on",
# 'emotions': {
#         'neutral': 0.600,
#         'curiosity': 0.299,
#         'confusion': 0.059
#     }
# }
# send = {'results': 
#         {'resources': [{'title': 'Probabilistic Machine Learning', 'url': 'https://www.reddit.com/r/deeplearning/comments/18ij68y/which_book_to_start/', 'type': 'Book'}, {'title': 'Deep Learning with Python', 'url': 'https://www.quora.com/What-are-the-best-books-about-deep-learning', 'type': 'Book'}, {'title': 'A Great Collection of Deep Learning (e)Books', 'url': 'https://github.com/ahkarami/Great-Deep-Learning-Books', 'type': 'Book'}, {'title': 'Deep Learning in Production Book', 'url': 'https://theaisummer.com/deep-learning-books-2022/', 'type': 'Book'}, {'title': 'Learn PyTorch for Deep Learning: Zero to Mastery', 'url': 'https://www.learnpytorch.io/', 'type': 'Course'}, {'title': 'Neural Networks and Deep Learning', 'url': 'http://neuralnetworksanddeeplearning.com/', 'type': 'Book'}, {'title': 'Deep Learning by Goodfellow, Bengio, and Courville', 'url': 'https://www.datacamp.com/blog/top-10-deep-learning-books-to-read-in-2022', 'type': 'Book'}, {'title': 'Dive into Deep Learning', 'url': 'https://d2l.ai/', 'type': 'Book'}, {'title': 'The Little Book of Deep Learning', 'url': 'https://fleuret.org/francois/lbdl.html', 'type': 'Book'}, {'title': 'fast.ai', 'url': 'https://course.fast.ai/', 'type': 'Course'}, {'title': 'Deep Learning', 'url': 'https://www.deeplearningbook.org/', 'type': 'Book'}, {'title': "DeepLearning.AI's resource center", 'url': 'https://www.deeplearning.ai/resources/', 'type': 'Course'}, {'title': 'Deep Learning', 'url': 'https://www.bishopbook.com/', 'type': 'Book'}, {'title': 'Deep Learning Crash Course', 'url': 'https://nostarch.com/deep-learning-crash-course', 'type': 'Book'}, {'title': 'Learning Deep Learning: Theory and Practice of Neural Networks, Computer Vision, Natural Language Processing, and Transformers Using TensorFlow', 'url': 'https://www.amazon.com/deep-learning-Books/s?k=deep+learning&rh=n%3A283155', 'type': 'Book'}], 'topic': 'Deep Learning', 'total_resources': 15, 'model_output': 'Successfully gathered learning resources for Deep Learning, including courses and books.  A diverse range of high-quality resources are provided.', 'specific_resources': ['Courses', 'Books'], 'module_name': 'learning_resources'},
#         'module_name': 'task_handler', 
#         'prompt': "Hey Robot, Provide me with some learning resources for Deep Learning, make sure to include some courses and books",
#         'emotions': {
#                 'neutral': 0.600,
#                 'curiosity': 0.299,
#                 'confusion': 0.059
#             }
# }
# send = {"error": "An error occurred while processing the request", "level": 2}
send = {"prompt": "Check my tasks for today"}

class GlobalMQTTHandler:
    """
    GlobalMQTTHandler listens on 'main/main' and publishes a list of predefined
    task payloads to 'task_handler/main' once triggered.
    """

    def __init__(self, sub_topic: str = "main/main", name: str = "global_publisher"):
        self._result = {}

        # self.__pub_topic = "postprocessing/data"
        self.__pub_topic = "task_classifier/prompt"
        # self.__pub_topic = "preprocessing/data"
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
