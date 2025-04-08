import paho.mqtt.client as mqtt
import json
from ast import literal_eval
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)


console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

class GlobalMQTTHandler:
    """
    GlobalMQTTHandler listens on 'server/main' and publishes a list of predefined
    task payloads to 'task_handler/global' once triggered.
    """

    def __init__(self, sub_topic: str = "server/main", name: str = "global_publisher"):
        self._result = {}

        self.__pub_topic = "postprocessing/prompt"
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
        return [
    {
        "method": "task_handler",
        "results": {
            "id": "a1ZMbFlOaHNXZV9xdkpIeQ",
            "name": "Schedule Doctor Appointment",
            "last_updated": "2025-04-08 05:09:39",
            "last_updated_relative": "2 seconds ago",
            "module_name": "tasks_api"
        }
    },
    {
        "method": "task_handler",
        "results": {
            "query": "What's the weather like on 2025-04-07?",
            "answer": "On April 7, 2025, expect a wet and cold weather with rain in Ohio. Temperatures will be low, and a freeze warning is in effect. The forecast indicates a cold front moving through the region.",
            "topic": "general",
            "time": 5.14,
            "module_name": "general_questions"
        }
    },
    {
        "method": "task_handler",
        "results": {
            "results": [
                {
                    "switch": "switch_1",
                    "status": "on",
                    "success": True
                }
            ],
            "module_name": "smart_home"
        }
    },
    {
        "method": "task_handler",
        "results": {
            "resources": [
                {
                    "title": "Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow",
                    "url": "https://www.amazon.com/Hands-On-Machine-Learning-Scikit-Learn-TensorFlow/dp/1492032646",
                    "type": "Books"
                },
                {
                    "title": "Deep Learning (Adaptive Computation and Machine Learning series)",
                    "url": "https://www.amazon.com/Deep-Learning-Adaptive-Computation-Machine-Learning/dp/0262035618",
                    "type": "Books"
                },
                {
                    "title": "Neural Networks and Deep Learning",
                    "url": "http://neuralnetworksanddeeplearning.com/",
                    "type": "Books"
                },
                {
                    "title": "Arxiv Sanity Preserver",
                    "url": "https://arxiv.org/",
                    "type": "Scientific Papers"
                },
                {
                    "title": "fast.ai",
                    "url": "https://www.fast.ai/",
                    "type": "Communities/Forums"
                },
                {
                    "title": "Distill.pub",
                    "url": "https://distill.pub/",
                    "type": "Blogs/Articles"
                },
                {
                    "title": "Papers with Code",
                    "url": "https://paperswithcode.com/sota",
                    "type": "Scientific Papers"
                },
                {
                    "title": "Dive into Deep Learning",
                    "url": "https://d2l.ai/",
                    "type": "Books"
                },
                {
                    "title": "Deep Learning Specialization - DeepLearning.AI",
                    "url": "https://www.deeplearning.ai/deep-learning-specialization/",
                    "type": "Courses"
                },
                {
                    "title": "Introduction to Deep Learning",
                    "url": "https://www.udacity.com/course/deep-learning-nanodegree--nd101",
                    "type": "Courses"
                },
                {
                    "title": "CS231n: Convolutional Neural Networks for Visual Recognition",
                    "url": "http://cs231n.stanford.edu/",
                    "type": "Courses"
                },
                {
                    "title": "Deep Learning from Scratch",
                    "url": "https://github.com/rasbt/deeplearning-models-pytorch",
                    "type": "Code Repositories"
                },
                {
                    "title": "Deep Learning with Python",
                    "url": "https://www.manning.com/books/deep-learning-with-python",
                    "type": "Books"
                },
                {
                    "title": "Deep Learning for Coders with fastai and PyTorch",
                    "url": "https://course.fast.ai/",
                    "type": "Courses"
                },
                {
                    "title": "Stanford CS224N: Natural Language Processing with Deep Learning",
                    "url": "http://web.stanford.edu/class/cs224n/",
                    "type": "Courses"
                }
            ],
            "topic": "Deep Learning",
            "total_resources": 15,
            "model_output": "I have compiled a list of high-quality learning resources for Deep Learning, including books and courses.  The resources cover various learning styles and levels of expertise.",
            "generation_time": 21.43,
            "cleaning_time": 0.0,
            "specific_resources": [
                "Courses",
                "Books"
            ],
            "module_name": "learning_resources"
        }
    }
]


    def publish_result(self, result: list):
        if result:
            payload = json.dumps(result)
            self.client.publish(self.__pub_topic, payload, self.__qos)
            logger.info(f"[{self.__name}] Published to '{self.__pub_topic}': {payload}")

    def start(self):
        self._result = self.execute_main({})
        for item in self._result:
            self.publish_result(item)
            
        logger.info(f"[{self.__name}] MQTT loop started.")
        self.client.loop_forever()

if __name__ == "__main__":
    handler = GlobalMQTTHandler()
    handler.start()
