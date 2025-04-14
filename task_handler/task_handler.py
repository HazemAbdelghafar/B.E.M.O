import sys
from pathlib import Path
import logging


# Add the root directory of the project to sys.path at the beginning
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utilities import BaseMQTTHandler

logging.basicConfig(format='%(asctime)s %(filename)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='./logging.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(__name__)


console_handler = logging.StreamHandler()
logger.addHandler(console_handler)


NAME = "task_handler"
SUB_TOPIC = "task_handler/main"

class TaskHandler(BaseMQTTHandler):
    def __init__(self):
        """
        Initialize the TaskHandler object.
        """
        super().__init__(sub_topic=SUB_TOPIC, name=NAME)
        
    def execute_main(self, input_data):
        """
        Execute the main functionality of the TaskHandler class.

        Args:
            input_data (dict | list): The input data to process.

        Returns:
            dict: The result of the processing.
        """
        # Check if input_data is a list
        preprocessed_data = input_data.get("preprocessed_data")
        
        if preprocessed_data:
            logger.info(f"Processing {len(preprocessed_data)} tasks")
                        
            # Iterate through each item in the list
            for item in preprocessed_data:
                method = item.get("method")

                if not method:
                    continue
                if method == "smart_home":
                    topic = "task_handler/smart_home"
                elif method == "todo":
                    topic = "task_handler/tasks_api"
                elif method == "general":
                    topic = "task_handler/general"
                elif method == "learning_resources":
                    topic = "task_handler/learning_resources"
                else:
                    logger.error(f"Unknown method: {method}")
                    self.publish_result({"error": "Unknown method", "level": 1})
                    continue
                
                # Publish the input data to the appropriate topic
                self.publish_result(item, topic)
        else:
            # if input data is not a list, send it to the main topic
            logger.info(f"Processing single task")
            
            result = input_data.get("results")
            
            if result:
                result = ({"results": result})
            else:
                result = {"results": input_data}
                
            self.publish_result(result)
             
        return None


if __name__ == "__main__":
    task_handler = TaskHandler()
    task_handler.start_mqtt()