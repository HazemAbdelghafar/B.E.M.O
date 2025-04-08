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
        self.results = []
        self.number_of_tasks = 0
        
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
            self.number_of_tasks = len(input_data)
            print(f"Number of tasks: {self.number_of_tasks}")
            
            # Iterate through each item in the list
            for item in input_data:
                method = item.get("method")
                if not method:
                    continue
                if method == "smart_home":
                    self.__pub_topic = "task_handler/smart_home"
                elif method == "todo":
                    self.__pub_topic = "task_handler/tasks_api"
                elif method == "general":
                    self.__pub_topic = "task_handler/general_questions"
                elif method == "learning_resources":
                    self.__pub_topic = "task_handler/learning_resources"
                else:
                    return {"status": "error", "message": f"Unknown method: {method}"}
                # Publish the input data to the appropriate topic
                self.publish_result(item)
                print(f"Published to {self.__pub_topic}: {item}")
        else:
            # if input data is not a list, process it as dictionary
            print(f"Processing single task")
            self.results.append(input_data)
             
            # If all tasks are completed, publish the results
            if self.number_of_tasks == len(self.results):
                self.__pub_topic = "server/main"
                self.publish_result({"method": NAME, "results": self.results})
                print(f"Published to {self.__pub_topic}: {self.results}")
                self.results = []
                self.number_of_tasks = 0                    
        return None

# payloads = [
#     {
#         "method": "smart_home",
#         "switch": ["switch_1"],
#         "status": ["on"],
#         "module_name": "preprocessing"
#     },
#     {
#         "method": "todo",
#         "list_all_tasks": False,
#         "object_type": "task",
#         "action": "insert",
#         "new_task_name": "Schedule doctor appointment",
#         "due_date": "2025-04-07T23:00:00",
#         "module_name": "preprocessing"
#     },
#     {
#         "method": "general",
#         "query": "What's the weather like on 2025-04-07?",
#         "topic": "general",
#         "module_name": "preprocessing"
#     },
#     {
#         "topic": "Deep Learning",
#         "specific_resources": ["Courses", "Books"]
#     }
# ]


if __name__ == "__main__":
    print("Starting Task Handler...")
    task_handler = TaskHandler()
    task_handler.start()