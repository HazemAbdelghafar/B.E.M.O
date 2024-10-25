from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from init_user import init_user


class TasksApi:
    def __init__(self, user_id: str):

        self.creds = init_user(user_id)
        self.service = build("tasks", "v1", credentials=self.creds)

    def get_all_tasks(self, max_results: int = 10):
        """
        This method gets all the tasks

        Args:
            max_results (int): The maximum number of tasks to get

        Returns:
            dict: The tasks
        """

        try:
            return self.service.tasklists().list(maxResults=max_results).execute()
        except HttpError as err:
            print(err)

    def get_task_list_by_id(self, task_list_id: str):
        """
        This method gets a task list

        Args:
            task_list_id (str): The task list id

        Returns:
            dict: The task list
        """

        try:
            return self.service.tasklists().get(tasklist=task_list_id).execute()
        except HttpError as err:
            print(err)
            return None

    def get_task_list_by_title(self, title: str) -> dict:
        """
        This method gets a task list by title

        Args:
            title (str): The task list title

        Returns:
            dict: The task list
        """

        task_lists = self.get_all_tasks()

        if task_lists:
            for item in task_lists.get("items", []):
                if item["title"] == title:
                    return item

        return None

    def delete_task_list_by_id(self, task_list_id: str):
        """
        This method deletes a task list

        Args:
            task_list_id (str): The task list id
        """

        try:
            self.service.tasklists().delete(tasklist=task_list_id).execute()
        except HttpError as err:
            print(err)
            return None

    def delete_task_list_by_title(self, title: str) -> bool:
        """
        This method deletes a task list by title

        Args:
            title (str): The task list title
        """

        task_list = self.get_task_list_by_title(title)

        if task_list:
            response = self.delete_task_list_by_id(task_list["id"])
            if response is None:
                return False
            else:
                return True
        else:
            return False


if __name__ == "__main__":
    # Initialize the tasks API
    tasks_api = TasksApi("0")

    task_lists = tasks_api.get_all_tasks()

    if task_lists:
        print("Task lists:")
        for item in task_lists.get("items", []):
            print(f"{item['title']} ({item['id']}) {item['updated']}")

    task_list = tasks_api.get_task_list_by_title("My Tasks")

    print("Task List by Title (My Tasks):")
    print(f"{task_list['title']} ({task_list['id']}) {task_list['updated']}")

    print("Deleting Task List by Title (Test List)...")
    print(tasks_api.delete_task_list_by_title("Test List"))
