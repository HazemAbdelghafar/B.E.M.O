import sys
from pathlib import Path

# Add the root directory of the project to sys.path at the beginning
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import BaseMQTTHandler

NAME = "task_handler"
SUB_TOPIC = "task_handler/global"

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
        if isinstance(input_data, list):
            print(f"Processing {len(input_data)} tasks")
                        
            # Iterate through each item in the list
            for item in input_data:
                method = item.get("method")

                if not method:
                    continue
                if method == "smart_home":
                    topic = "task_handler/smart_home"
                elif method == "todo":
                    topic = "task_handler/tasks_api"
                elif method == "general":
                    topic = "task_handler/general_questions"
                elif method == "learning_resources":
                    topic = "task_handler/learning_resources"
                else:
                    return {"error": f"Unknown method: {method}"}
                # Publish the input data to the appropriate topic
                self.publish_result(item, topic)
                
        # if input data is not a list, process it as dictionary
        else:
            print("Processing single task")
            self.publish_result({"method": NAME, "results": input_data},  "server/main")
             
        return None


if __name__ == "__main__":
    task_handler = TaskHandler()
    task_handler.start()