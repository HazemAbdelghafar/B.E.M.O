from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from init_user import init_user
from pprint import pprint
from utils import RFC3339_to_datetime


class TasksApi:
    def __init__(self, user_id: str):

        self._creds = init_user(user_id)
        self._service = build("tasks", "v1", credentials=self._creds)

    def list_task_lists_all(self, max_results: int = 10) -> list:
        """
        This method gets all the task lists

        Args:
            max_results (int): The maximum number of tasks to get

        Returns:
            dict: The tasks lists or None if no task lists were found
        """

        try:
            items = (
                self._service.tasklists()
                .list(maxResults=max_results)
                .execute()["items"]
            )

            for item in items:
                item["updated"] = RFC3339_to_datetime(item["updated"])

            return items
        except HttpError as err:
            print(err)
            return None

    def _get_task_list_by_id(self, task_list_id: str) -> dict:
        """
        This method gets a task list by id

        Args:
            task_list_id (str): The task list id

        Returns:
            dict: The task list or None if the task list was not found
        """

        try:
            return self._service.tasklists().get(tasklist=task_list_id).execute()
        except HttpError as err:
            print(err)
            return None

    def get_task_list_by_title(self, title: str) -> tuple:
        """
        This method gets a task list by title

        Args:
            title (str): The task list title

        Returns:
            tuple: The task list id, title, and updated time or None if the task list was not found
        """

        task_lists = self.list_task_lists_all()

        if task_lists:
            for item in task_lists:
                if item["title"] == title:
                    return (
                        item["id"],
                        item["title"],
                        RFC3339_to_datetime(item["updated"]),
                    )

        return None, None, None

    def _delete_task_list_by_id(self, task_list_id: str) -> bool:
        """
        This method deletes a task list by id

        Args:
            task_list_id (str): The task list id

        Returns:
            bool: True if the task list was deleted, False otherwise
        """

        try:
            self._service.tasklists().delete(tasklist=task_list_id).execute()
            return True
        except HttpError as err:
            print(err)
            return False

    def delete_task_list_by_title(self, title: str) -> bool:
        """
        This method deletes a task list by title

        Args:
            title (str): The task list title

        Returns:
            bool: True if the task list was deleted, False otherwise
        """

        id, _, _ = self.get_task_list_by_title(title)

        if id:
            response = self._delete_task_list_by_id(id)
            return response
        else:
            return False

    def insert_task_list(self, title: str) -> tuple:
        """
        This method inserts a task list

        Args:
            title (str): The task list title

        Returns:
            tuple: The task list id, title, and updated time or None if the task list was not inserted
        """

        task_list = {"title": title}

        try:
            result = self._service.tasklists().insert(body=task_list).execute()
            return result["id"], result["title"], RFC3339_to_datetime(result["updated"])

        except HttpError as err:
            print(err)
            return None, None, None

    def _rename_task_list_id(self, task_list_id: str, task_list_name: str) -> tuple:
        """
        This method renames a task list by id

        Args:
            task_list_id (str): The task list id
            body (dict): The task list body

        Returns:
            tuple: The task list id, title, and updated time or None if the task list was not patched
        """

        body = {"title": task_list_name}

        try:
            result = (
                self._service.tasklists()
                .patch(tasklist=task_list_id, body=body)
                .execute()
            )
            return result["id"], result["title"], RFC3339_to_datetime(result["updated"])

        except HttpError as err:
            print(err)
            return None, None, None

    def rename_task_list_by_title(self, old_title: str, new_title: str) -> tuple:
        """
        This method patches a task list by title

        Args:
            title (str): The task list title
            new_title (str): The new task list title

        Returns:
            tuple: The task list id, title, and updated time or None if the task list was not patched
        """

        id, _, _ = self.get_task_list_by_title(old_title)

        if id:
            return self._rename_task_list_id(id, new_title)
        else:
            return None, None, None

    def _list_tasks_by_task_list_id(
        self, task_list_id: str, max_results: int = 10
    ) -> list:
        """
        This method gets all the tasks

        Args:
            task_list_id (str): The task list id
            max_results (int): The maximum number of tasks to get

        Returns:
            list: The tasks or None if no tasks were found
        """

        try:
            return (
                self._service.tasks()
                .list(tasklist=task_list_id, maxResults=max_results)
                .execute()["items"]
            )
        except HttpError as err:
            print(err)
            return None

    def list_tasks_by_task_list_title(self, title: str, max_results: int = 10) -> list:
        """
        This method gets all the tasks

        Args:
            title (str): The task list title
            max_results (int): The maximum number of tasks to get

        Returns:
            list: The tasks or None if no tasks were found
        """

        id, _, _ = self.get_task_list_by_title(title)

        if id:
            return self._list_tasks_by_task_list_id(id, max_results)
        else:
            return None

    def list_tasks_all(self, max_results: int = 10) -> list:
        """
        This method gets all the tasks

        Args:
            max_results (int): The maximum number of tasks to get

        Returns:
            list: The tasks or None if no tasks were found
        """

        task_lists = self.list_task_lists_all()

        if task_lists:
            tasks = []
            for item in task_lists:
                tasks.extend(self._list_tasks_by_task_list_id(item["id"], max_results))
            return tasks


if __name__ == "__main__":

    new_list_name = "Test List"
    patched_list_name = "New Test List"

    # Initialize the tasks API
    tasks_api = TasksApi("0")

    print("Task Lists:")
    task_lists = tasks_api.list_task_lists_all()

    if task_lists:
        for item in task_lists:
            print(f"{item['title']} ({item['id']}) {item['updated']}")

    else:
        print("No task lists found.")

    print("Task List by Title (My Tasks):")
    id, title, updated_time = tasks_api.get_task_list_by_title("My Tasks")
    print(f"{title} ({id}) {updated_time}")

    print(f"Inserting Task List ({new_list_name})...")
    id, title, updated_time = tasks_api.insert_task_list(new_list_name)
    print(f"{title} ({id}) {updated_time}")

    print(f"Patch Task List ({patched_list_name})...")
    id, title, updated_time = tasks_api.rename_task_list_by_title(
        new_list_name, patched_list_name
    )
    print(f"{title} ({id}) {updated_time}")

    print(f"Delete Task List ({patched_list_name})...")
    result = tasks_api.delete_task_list_by_title(patched_list_name)
    if result:
        print(f"Task List ({patched_list_name}) was deleted.")
    else:
        print(f"Task List ({patched_list_name}) was not deleted.")

    print("Task Lists after deletion:")
    task_lists = tasks_api.list_task_lists_all()

    if task_lists:
        for item in task_lists:
            print(f"{item['title']} ({item['id']}) {item['updated']}")

    else:
        print("No task lists found.")

    print("All Tasks:")
    tasks = tasks_api.list_tasks_all()

    if tasks:
        print("Tasks:")
        pprint(tasks)
        # for item in tasks.get("items", []):
        #     print(f"{item['title']} ({item['id']}) {item['updated']}")
