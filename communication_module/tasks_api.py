from pprint import pprint
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from init_user import init_user
from utils import RFC3339_to_date, datetime_to_RFC3339


DEFAULT_NOTE = "CREATED BY BEMO"


class TasksApi:
    def __init__(self, user_id: str) -> None:
        """
        This method initializes the tasks API

        Args:
            user_id (str): The user id

        Returns:
            None
        """

        self._creds = init_user(user_id)
        self._service = build("tasks", "v1", credentials=self._creds)

    def list_task_lists_all(self, max_results: int = 10) -> list:
        """
        This method gets all the task lists

        Args:
            max_results (int): The maximum number of tasks to get (default is 10)

        Returns:
            list: The task lists or None if no task lists were found
        """

        return_list = []

        try:
            task_lists = (
                self._service.tasklists()
                .list(maxResults=max_results)
                .execute()["items"]
            )

            for item in task_lists:
                item["updated"] = RFC3339_to_date(item["updated"])
                return_list.append(
                    {
                        "id": item["id"],
                        "name": item["title"],
                        "last_updated": item["updated"],
                    }
                )

            return return_list
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

    def get_task_lists_by_name(self, name: str) -> list:
        """
        This method gets a task list by title

        Args:
            name (str): The task list title

        Returns:
            list: The task list id, title, and updated time or None if the task list was not found
        """

        task_lists = self.list_task_lists_all()

        return_list = []

        if task_lists:
            for item in task_lists:
                if item["name"] == name:
                    return_list.append(
                        {
                            "id": item["id"],
                            "name": item["name"],
                            "last_updated": item["last_updated"],
                        }
                    )

            return return_list

        else:
            return None

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

    def delete_task_lists_by_name(self, name: str) -> bool:
        """
        This method deletes a task list by title

        Args:
            name (str): The task list title

        Returns:
            bool: True if the task list was deleted, False otherwise
        """

        task_lists = self.get_task_lists_by_name(name)

        if task_lists:
            responses = []
            for item in task_lists:
                id = item["id"]
                response = self._delete_task_list_by_id(id)
                responses.append(response)
                return all(responses)
        else:
            return False

    def insert_task_list(self, title: str) -> dict:
        """
        This method inserts a task list

        Args:
            title (str): The task list title

        Returns:
            dict: The task list id, title, and updated time or None if the task list was not inserted
        """

        body = {"title": title}

        try:
            task_list = self._service.tasklists().insert(body=body).execute()
            return {
                "id": task_list["id"],
                "name": task_list["title"],
                "last_updated": RFC3339_to_date(task_list["updated"]),
            }

        except HttpError as err:
            print(err)
            return None, None, None

    def _patch_task_list_id(self, task_list_id: str, task_list_name: str) -> dict:
        """
        This method renames a task list by id

        Args:
            task_list_id (str): The task list id
            body (dict): The task list body

        Returns:
            dict: The task list id, title, and updated time or None if the task list was not patched
        """

        body = {"title": task_list_name}

        try:
            task_list = (
                self._service.tasklists()
                .patch(tasklist=task_list_id, body=body)
                .execute()
            )
            return {
                "id": task_list["id"],
                "name": task_list["title"],
                "last_updated": RFC3339_to_date(task_list["updated"]),
            }

        except HttpError as err:
            print(err)
            return None, None, None

    def patch_task_lists_by_name(self, old_name: str, new_name: str) -> list:
        """
        This method patches a task list by title

        Args:
            old_name (str): The task list title
            new_name (str): The new task list title

        Returns:
            list: The task list id, title, and updated time or None if the task list was not patched
        """

        task_lists = self.get_task_lists_by_name(old_name)

        if task_lists:
            return_list = []
            for item in task_lists:
                id = item["id"]
                response = self._patch_task_list_id(id, new_name)
                return_list.append(
                    {
                        "id": response["id"],
                        "name": response["name"],
                        "last_updated": response["last_updated"],
                    }
                )
            return return_list
        else:
            return None

    def _list_tasks_by_task_list_id(
        self,
        task_list_id: str,
        max_results: int = 10,
        show_completed: bool = True,
        show_deleted: bool = True,
        show_hidden: bool = True,
    ) -> dict:
        """
        This method gets all the tasks

        Args:
            task_list_id (str): The task list id
            max_results (int): The maximum number of tasks to get (default is 10)
            show_completed (bool): Whether to show completed tasks (default is True)
            show_deleted (bool): Whether to show deleted tasks (default is True)
            show_hidden (bool): Whether to show hidden tasks (default is True)

        Returns:
            dict: The tasks or None if no tasks were found
        """

        try:
            return (
                self._service.tasks()
                .list(
                    tasklist=task_list_id,
                    maxResults=max_results,
                    showCompleted=show_completed,
                    showDeleted=show_deleted,
                    showHidden=show_hidden,
                )
                .execute()
            )
        except HttpError as err:
            print(err)
            return None

    def list_tasks_by_task_list_name(
        self,
        name: str,
        max_results: int = 10,
        show_completed: bool = True,
        show_deleted: bool = True,
        show_hidden: bool = True,
    ) -> list:
        """
        This method gets all the tasks

        Args:
            title (str): The task list title
            max_results (int): The maximum number of tasks to get
            show_completed (bool): Whether to show completed tasks
            show_deleted (bool): Whether to show deleted tasks
            show_hidden (bool): Whether to show hidden tasks

        Returns:
            list: The tasks or None if no tasks were found
        """

        task_lists = self.get_task_lists_by_name(name)

        return_list = []

        if task_lists:
            for item in task_lists:
                id = item["id"]
                return_list.append(
                    self._list_tasks_by_task_list_id(
                        id, max_results, show_completed, show_deleted, show_hidden
                    )["items"]
                )
            return return_list
        else:
            return None

    def list_tasks_all(
        self,
        max_results: int = 10,
        show_completed: bool = True,
        show_deleted: bool = True,
        show_hidden: bool = True,
    ) -> list:
        """
        This method gets all the tasks

        Args:
            max_results (int): The maximum number of tasks to get (default is 10)
            show_completed (bool): Whether to show completed tasks (default is True)
            show_deleted (bool): Whether to show deleted tasks (default is True)
            show_hidden (bool): Whether to show hidden tasks (default is True)

        Returns:
            list: The tasks or None if no tasks were found
        """

        return_list = []

        task_lists = self.list_task_lists_all()

        if task_lists:
            for item in task_lists:
                tasks = self._list_tasks_by_task_list_id(
                    item["id"], max_results, show_completed, show_deleted, show_hidden
                )["items"]
                for task in tasks:
                    try:
                        if not task["deleted"]:
                            continue
                    except KeyError:
                        pass
                    else:
                        continue

                    return_list.append(
                        {
                            "id": task["id"],
                            "list_id": item["id"],
                            "name": task["title"],
                            "list_name": item["name"],
                            "last_updated": task["updated"],
                            "due_date": task.get("due", None),
                            "completed_date": task.get("completed", None),
                            "is_done": (
                                True if task.get("status") == "completed" else False
                            ),
                            "notes": task.get("notes", None),
                            "parent_id": task.get("parent", None),
                        }
                    )
                    return_list[-1]["last_updated"] = RFC3339_to_date(
                        return_list[-1]["last_updated"]
                    )

                    if return_list[-1]["due_date"]:
                        return_list[-1]["due_date"] = RFC3339_to_date(
                            return_list[-1]["due_date"]
                        )

                    if return_list[-1]["completed_date"]:
                        return_list[-1]["completed_date"] = RFC3339_to_date(
                            return_list[-1]["completed_date"]
                        )

                    if return_list[-1]["parent_id"]:
                        return_list[-1]["parent_title"] = self._get_task_by_id(
                            item["id"], return_list[-1]["parent_id"]
                        )["title"]
                    else:
                        return_list[-1]["parent_title"] = None

            return return_list

        else:
            return None

    def _get_task_by_id(self, task_list_id: str, task_id: str) -> dict:
        """
        This method gets a task by id

        Args:
            task_list_id (str): The task list id
            task_id (str): The task id

        Returns:
            dict: The task or None if the task was not found
        """

        try:
            return (
                self._service.tasks().get(tasklist=task_list_id, task=task_id).execute()
            )
        except HttpError as err:
            print(err)
            return None

    def get_tasks_by_name(self, task_name: str) -> list:
        """
        This method gets a task by title

        Args:
            task_name (str): The task title

        Returns:
            list: The tasks or None if no tasks were found
        """

        return_list = []

        tasks = self.list_tasks_all()

        if tasks:
            for item in tasks:
                if item["name"] == task_name:
                    return_list.append(item)
            return return_list
        else:
            return None

    def _delete_task_by_id(self, task_list_id: str, task_id: str) -> bool:
        """
        This method deletes a task by id

        Args:
            task_list_id (str): The task list id
            task_id (str): The task id

        Returns:
            bool: True if the task was deleted, False otherwise
        """

        try:
            self._service.tasks().delete(tasklist=task_list_id, task=task_id).execute()
            return True
        except HttpError as err:
            print(err)
            return False

    def delete_tasks_by_name(self, task_name: str) -> bool:
        """
        This method deletes a task by title

        Args:
            task_name (str): The task title

        Returns:
            bool: True if the task was deleted, False otherwise
        """

        tasks = self.get_tasks_by_name(task_name)

        if tasks:
            responses = []
            for task in tasks:
                id = task["id"]
                list_id = task["list_id"]
                response = self._delete_task_by_id(list_id, id)
                responses.append(response)
            return all(responses)
        else:
            return False

    def _insert_task_by_list_id_parent_id(
        self,
        list_id: str,
        name: str,
        due_date: datetime = None,
        notes: str = None,
        parent_id: str = None,
    ) -> dict:
        """
        This method inserts a task

        Args:
            list_id (str): The task list id
            name (str): The task title
            due_date (datetime): The task due date (default is None)
            notes (str): The task notes (default is None)
            parent_id (str): The task parent id (default is None)

        Returns:
            dict: The task id, title, and updated time or None if the task was not inserted
        """

        move_task = False

        body = {"title": name}

        if due_date:
            body["due"] = datetime_to_RFC3339(due_date)

        if notes:
            body["notes"] = notes + ", " + DEFAULT_NOTE
        else:
            body["notes"] = DEFAULT_NOTE

        if parent_id:
            move_task = True

        try:
            task = self._service.tasks().insert(tasklist=list_id, body=body).execute()

            if move_task:
                self._move_task_by_list_id_task_id_parent_id(
                    list_id, task["id"], parent_id
                )

            return {
                "id": task["id"],
                "name": task["title"],
                "last_updated": RFC3339_to_date(task["updated"]),
            }

        except HttpError as err:
            print(err)
            return None

    def insert_task_by_list_name_parent_name(
        self,
        list_name: str,
        name: str,
        due_date: str = None,
        notes: str = None,
        parent_name: str = None,
    ) -> dict:
        """
        This method inserts a task

        Args:
            list_name (str): The task list title
            name (str): The task title
            due_date (str): The task due date (default is None)
            notes (str): The task notes (default is None)
            parent_name (str): The task parent title (default is None)

        Returns:
            dict: The task id, title, and updated time or None if the task was not inserted
        """

        task_lists = self.get_task_lists_by_name(list_name)
        try:
            task_list_id = task_lists[0]["id"]
        except IndexError:
            return None

        if parent_name:
            parent_tasks = self.get_tasks_by_name(parent_name)
            try:
                parent_id = parent_tasks[0]["id"]
            except IndexError:
                parent_id = None

        else:
            parent_id = None

        if due_date:
            due_date = datetime.fromisoformat(due_date)

        if task_lists:
            response = self._insert_task_by_list_id_parent_id(
                task_list_id, name, due_date, notes, parent_id
            )
            return {
                "id": response["id"],
                "name": response["name"],
                "last_updated": response["last_updated"],
            }

        else:
            return None

    def _move_task_by_list_id_task_id_parent_id(
        self,
        old_list_id: str,
        task_id: str,
        parent_id: str = None,
        new_list_id: str = None,
    ) -> bool:
        """
        This method moves a task

        Args:
            list_id (str): The task list id
            task_id (str): The task id
            parent_id (str): The task parent id (default is None)
            new_list_id (str): The new task list id (default is None)

        Returns:
            bool: True if the task was moved, False otherwise
        """

        if parent_id == None and new_list_id == None:
            return False

        try:
            self._service.tasks().move(
                tasklist=old_list_id,
                task=task_id,
                parent=parent_id,
                previous=None,
                destinationTasklist=new_list_id,
            ).execute()
            return True
        except HttpError as err:
            print(err)
            return False

    def move_task_by_list_name_task_name_parent_name(
        self,
        old_list_name: str,
        task_name: str,
        parent_name: str = None,
        new_list_name: str = None,
    ) -> bool:
        """
        This method moves a task

        Args:
            list_name (str): The task list title
            task_name (str): The task title
            parent_name (str): The task parent title (default is None)
            new_list_name (str): The new task list title (default is None)

        Returns:
            bool: True if the task was moved, False otherwise
        """

        task_lists = self.get_task_lists_by_name(old_list_name)
        try:
            task_list_id = task_lists[0]["id"]
        except IndexError:
            return False

        tasks = self.get_tasks_by_name(task_name)
        try:
            task_id = tasks[0]["id"]
        except IndexError:
            return False

        if parent_name:
            parent_tasks = self.get_tasks_by_name(parent_name)
            try:
                parent_id = parent_tasks[0]["id"]
            except IndexError:
                parent_id = None
        else:
            parent_id = None

        if new_list_name:
            new_list = self.get_task_lists_by_name(new_list_name)
            try:
                new_list_id = new_list[0]["id"]
            except IndexError:
                new_list_id = None
        else:
            new_list_id = None

        return self._move_task_by_list_id_task_id_parent_id(
            task_list_id, task_id, parent_id, new_list_id
        )

    def _patch_task_by_list_id_task_id(
        self,
        list_id: str,
        task_id: str,
        new_task_name: str = None,
        due_date: datetime = None,
        notes: str = None,
        parent_id: str = None,
        is_done: bool = None,
    ) -> dict:
        """
        This method patches a task by id

        Args:
            list_id (str): The task list id
            task_id (str): The task id
            new_task_name (str): The new task title (default is None)
            due_date (datetime): The new task due date (default is None)
            notes (str): The new task notes (default is None)
            parent_id (str): The new task parent id (default is None)
            is_done (bool): Whether the task is done (default is None)

        Returns:
            dict: The task id, title, and updated time or None if the task was not patched
        """

        body = {}

        if new_task_name:
            body["title"] = new_task_name

        if due_date:
            body["due"] = datetime_to_RFC3339(due_date)

        if notes:
            body["notes"] = notes + ", " + DEFAULT_NOTE
        else:
            body["notes"] = DEFAULT_NOTE

        if parent_id:
            self._move_task_by_list_id_task_id_parent_id(list_id, task_id, parent_id)

        if is_done != None:
            if is_done:
                body["status"] = "completed"
                body["completed"] = datetime_to_RFC3339(datetime.now())
            else:
                body["status"] = "needsAction"
                body["completed"] = None

        try:
            task = (
                self._service.tasks()
                .patch(tasklist=list_id, task=task_id, body=body)
                .execute()
            )
            return {
                "id": task["id"],
                "name": task["title"],
                "last_updated": RFC3339_to_date(task["updated"]),
            }

        except HttpError as err:
            print(err)
            return None

    def patch_task_by_list_name_task_name(
        self,
        list_name: str,
        task_name: str,
        new_task_name: str = None,
        due_date: str = None,
        notes: str = None,
        parent_name: str = None,
        is_done: bool = None,
    ) -> dict:
        """
        This method patches a task by title

        Args:
            list_name (str): The task list title
            task_name (str): The task title
            new_task_name (str): The new task title (default is None)
            due_date (str): The new task due date (default is None)
            notes (str): The new task notes (default is None)
            parent_name (str): The new task parent title (default is None)

        Returns:
            dict: The task id, title, and updated time or None if the task was not patched
        """

        task_lists = self.get_task_lists_by_name(list_name)
        try:
            task_list_id = task_lists[0]["id"]
        except IndexError:
            return None

        tasks = self.get_tasks_by_name(task_name)
        try:
            task_id = tasks[0]["id"]
        except IndexError:
            return None

        if parent_name:
            parent_tasks = self.get_tasks_by_name(parent_name)
            try:
                parent_id = parent_tasks[0]["id"]
            except IndexError:
                parent_id = None
        else:
            parent_id = None

        if due_date:
            due_date = datetime.fromisoformat(due_date)

        response = self._patch_task_by_list_id_task_id(
            task_list_id, task_id, new_task_name, due_date, notes, parent_id, is_done
        )
        return {
            "id": response["id"],
            "name": response["name"],
            "last_updated": response["last_updated"],
        }


if __name__ == "__main__":

    new_list_name = "Test List"
    patched_list_name = "New Test List"

    # Initialize the tasks API
    tasks_api = TasksApi("0")

    print("Task Lists:")
    task_lists = tasks_api.list_task_lists_all()

    if task_lists:
        for item in task_lists:
            print(f"{item['name']} ({item['id']}) {item['last_updated']}")

    else:
        print("No task lists found.")

    print("Task List by Title (My Tasks):")
    task_lists = tasks_api.get_task_lists_by_name("My Tasks")
    for item in task_lists:
        print(f"{item['name']} ({item['id']}) {item['last_updated']}")

    print(f"Inserting Task List ({new_list_name})...")
    task_list = tasks_api.insert_task_list(new_list_name)
    print(f"{task_list['name']} ({task_list['id']}) {task_list['last_updated']}")

    print(f"Patch Task List ({patched_list_name})...")
    task_lists = tasks_api.patch_task_lists_by_name(new_list_name, patched_list_name)
    for item in task_lists:
        print(f"{item['name']} ({item['id']}) {item['last_updated']}")

    print(f"Delete Task List ({patched_list_name})...")
    result = tasks_api.delete_task_lists_by_name(patched_list_name)
    if result:
        print(f"Task List ({patched_list_name}) was deleted.")
    else:
        print(f"Task List ({patched_list_name}) was not deleted.")

    print("Task Lists after deletion:")
    task_lists = tasks_api.list_task_lists_all()

    if task_lists:
        for item in task_lists:
            print(f"{item['name']} ({item['id']}) {item['last_updated']}")

    else:
        print("No task lists found.")

    print("All Tasks:")
    tasks = tasks_api.list_tasks_all()

    if tasks:
        print("Tasks:")
        pprint(tasks)
    else:
        print("No tasks found.")

    print("Task by Name (Test 1):")
    task = tasks_api.get_tasks_by_name("Test 1")

    if task:
        pprint(task)
    else:
        print("No task found.")

    print(f"Delete Task (Test)...")
    result = tasks_api.delete_tasks_by_name("Test")

    if result:
        print(f"Task (Test) was deleted.")
    else:
        print(f"Task (Test) was not deleted.")

    print("Insert Task (Test 3)...")
    tasks = tasks_api.insert_task_by_list_name_parent_name(
        "New Test List",
        "Test 3",
        "2024-11-01T00:00:00",
        "Test 3 Notes",
        "Test 0",
    )

    if tasks:
        print(f"{tasks['name']} ({tasks['id']}) {tasks['last_updated']}")
    else:
        print("Task (Test 3) was not inserted.")

    print("Move Task (Test 3) under Test 1...")
    result = tasks_api.move_task_by_list_name_task_name_parent_name(
        "New Test List",
        "Test 3",
        parent_name="Test 1",
    )
    if result:
        print(f"Task (Test 3) was moved.")
    else:
        print(f"Task (Test 3) was not moved.")

    print("Move Task (Test 3) from New Test List to Test List...")
    result = tasks_api.move_task_by_list_name_task_name_parent_name(
        "New Test List",
        "Test 3",
        new_list_name="My Tasks",
    )
    if result:
        print(f"Task (Test 3) was moved.")
    else:
        print(f"Task (Test 3) was not moved.")

    print("Patch Task (Test 3)...")
    task = tasks_api.patch_task_by_list_name_task_name(
        "New Test List",
        "Test 3",
        new_task_name="Test 3 Patched",
        due_date="2024-11-01T00:00:00",
        notes="Test 3 Patched Notes",
        is_done=True,
    )
    if task:
        print(f"{task['name']} ({task['id']}) {task['last_updated']}")
    else:
        print("Task (Test 3) was not patched.")
