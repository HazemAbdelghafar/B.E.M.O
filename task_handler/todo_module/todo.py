import sys
from pathlib import Path
from datetime import datetime
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from init_user import init_user_google

from helper_functions import (
    RFC3339_to_date_and_time,
    datetime_to_RFC3339,
    RFC3339_to_relative_time,
    RFC3339_change_timezones,
    date_and_time_to_datetime,
    get_current_time,
)
import logging


# Add the root directory of the project to sys.path at the beginning
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utilities import BaseMQTTHandler, UserData

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    filename="./logging.log",
    encoding="utf-8",
    level=logging.DEBUG,
)


console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

DEFAULT_NOTE = "\n\nB.E.M.O"
DEFAULT_PATH = os.path.dirname(__file__)
DEFAULT_TIMEZONE = UserData().get_user_data("timezone")


class TasksApi(BaseMQTTHandler):
    """
    This class now inherits from BaseMQTTHandler to enable MQTT functionality.
    """

    def __init__(self, robot_id: str, timezone: str = DEFAULT_TIMEZONE) -> None:
        """
        This method initializes the tasks API

        Args:
            user_id (str): The user id
            timezone (str): The timezone (default is Africa/Cairo)

        Returns:
            None
        """
        # Initialize BaseMQTTHandler with MQTT topics
        super().__init__(sub_topic="task_handler/todo", name="todo")

        self._timezone = timezone
        self._robot_id = robot_id
        self.is_initialized = False

        self._init_tasks_api()

    def _init_tasks_api(self):
        try:
            self._creds = init_user_google(self._robot_id)
            self._service = build("tasks", "v1", credentials=self._creds)
        except Exception as e:
            logger.error(f"Error initializing tasks API: {e}")
            self.is_initialized = False
            return

        self.is_initialized = True

    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.

        Args:
            input_data (dict): The input data to process.

        Returns:
            dict: The result of the task operation.
        """
        if not self.is_initialized:
            logger.error("Tasks API not initialized")
            return {"error": "Tasks API not initialized", "level": 2}

        if not isinstance(input_data, dict):
            result = {"error": "Invalid input data", "level": 2}
            logger.error(f"Error processing input data: {result}")
        else:
            try:
                result = self(input_data)
                logger.info(f"Result: {result}")
            except Exception as e:
                logger.error(f"Error processing input data: {e}")
                result = {"error": str(e), "level": 2}

        if isinstance(result, list):
            result = {"result_list": result}

        self.publish_result(result, "task_handler/main")

        return None

    # Task Lists
    ####################################################################################################

    # Task Lists (List)
    ####################################################################################################
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
                changed_time = RFC3339_change_timezones(
                    item["updated"], to_timezone=self._timezone
                )

                date, time = RFC3339_to_date_and_time(changed_time)
                return_list.append(
                    {
                        "id": item["id"],
                        "name": item["title"],
                        "last_updated": date + time,
                        "last_updated_relative": RFC3339_to_relative_time(
                            changed_time, self._timezone
                        ),
                    }
                )

            return return_list
        except HttpError as err:
            logger.error(err)
            return None

    # Task Lists (Get)
    ####################################################################################################
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
            logger.error(err)
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

        name = name.lower().strip()

        if task_lists:
            for item in task_lists:
                if item["name"].lower().strip() == name:
                    return_list.append(
                        {
                            "id": item["id"],
                            "name": item["name"],
                            "last_updated": item["last_updated"],
                            "last_updated_relative": item["last_updated_relative"],
                        }
                    )

            return return_list

        else:
            return None

    # Task Lists (Delete)
    ####################################################################################################
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
            logger.error(err)
            return False

    def delete_task_lists_by_name(self, name: str) -> bool:
        """
        This method deletes a task list by title

        Args:
            name (str): The task list title

        Returns:
            bool: A dictionary containing the success status or None if the task list was not deleted
        """

        task_lists = self.get_task_lists_by_name(name)

        if task_lists:
            responses = []
            for item in task_lists:
                id = item["id"]
                response = self._delete_task_list_by_id(id)
                responses.append(response)
                if all(responses):
                    return {"success": True}
                else:
                    return None
        else:
            return None

    # Task Lists (Insert)
    ####################################################################################################
    def insert_task_list(self, title: str) -> dict:
        """
        This method inserts a task list

        Args:
            title (str): The task list title

        Returns:
            dict: The task list id, title, and updated time or None if the task list was not inserted
        """

        body = {"title": title.strip().title()}

        try:
            task_list = self._service.tasklists().insert(body=body).execute()
            changed_time = RFC3339_change_timezones(
                task_list["updated"], to_timezone=self._timezone
            )
            date, time = RFC3339_to_date_and_time(changed_time)
            return {
                "id": task_list["id"],
                "name": task_list["title"],
                "last_updated": date + time,
                "last_updated_relative": RFC3339_to_relative_time(
                    changed_time, self._timezone
                ),
            }

        except HttpError as err:
            logger.infor.info(err)
            return None

    # Task Lists (Update)
    ####################################################################################################
    def _update_task_list_id(self, task_list_id: str, new_task_list_name: str) -> dict:
        """
        This method renames a task list by id

        Args:
            task_list_id (str): The task list id
            body (dict): The task list body

        Returns:
            dict: The task list id, title, and updated time or None if the task list was not updated
        """

        body = {"title": new_task_list_name.strip().title()}

        try:
            task_list = (
                self._service.tasklists()
                .patch(tasklist=task_list_id, body=body)
                .execute()
            )
            changed_time = RFC3339_change_timezones(
                task_list["updated"], to_timezone=self._timezone
            )
            date, time = RFC3339_to_date_and_time(changed_time)
            return {
                "id": task_list["id"],
                "name": task_list["title"],
                "last_updated": date + time,
                "last_updated_relative": RFC3339_to_relative_time(
                    changed_time, self._timezone
                ),
            }

        except HttpError as err:
            logger.error(err)
            return None

    def update_task_lists_by_name(self, old_name: str, new_name: str) -> list:
        """
        This method updates a task list by title

        Args:
            old_name (str): The task list title
            new_name (str): The new task list title

        Returns:
            list: The task list id, title, and updated time or None if the task list was not updated
        """

        task_lists = self.get_task_lists_by_name(old_name)

        if task_lists:
            return_list = []
            for item in task_lists:
                id = item["id"]
                response = self._update_task_list_id(id, new_name)
                if response:
                    return_list.append(
                        {
                            "id": response["id"],
                            "name": response["name"],
                            "last_updated": response["last_updated"],
                            "last_updated_relative": response["last_updated_relative"],
                        }
                    )
            if return_list:
                return return_list
            else:
                return None
        else:
            return None

    # Tasks
    ####################################################################################################

    # Tasks (List)
    ####################################################################################################
    def _list_tasks_by_task_list_id(
        self,
        task_list_id: str,
        max_results: int = 10,
        show_completed: bool = True,
        show_deleted: bool = False,
        show_hidden: bool = False,
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
            logger.error(err)
            return None

    def list_tasks_by_task_list_name(
        self,
        name: str,
        max_results: int = 10,
        show_completed: bool = True,
        show_deleted: bool = False,
        show_hidden: bool = False,
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
                            "last_updated_relative": None,
                            "completed_date_relative": None,
                            "due_date_relative": None,
                            "parent_title": None,
                        }
                    )

                    RFC_time_updated = task["updated"]
                    changed_time_updated = RFC3339_change_timezones(
                        RFC_time_updated, to_timezone=self._timezone
                    )
                    date, time = RFC3339_to_date_and_time(changed_time_updated)

                    return_list[-1]["last_updated"] = date + time
                    return_list[-1]["last_updated_relative"] = RFC3339_to_relative_time(
                        changed_time_updated, self._timezone
                    )

                    if return_list[-1]["due_date"]:
                        RFC_time_due = return_list[-1]["due_date"]
                        changed_time_due = RFC3339_change_timezones(
                            RFC_time_due, to_timezone=self._timezone
                        )
                        date, time = RFC3339_to_date_and_time(changed_time_due)
                        return_list[-1]["due_date"] = date + time
                        return_list[-1]["due_date_relative"] = RFC3339_to_relative_time(
                            changed_time_due, self._timezone
                        )

                    if return_list[-1]["completed_date"]:
                        RFC_time_completed = return_list[-1]["completed_date"]
                        changed_time_completed = RFC3339_change_timezones(
                            RFC_time_completed, to_timezone=self._timezone
                        )
                        date, time = RFC3339_to_date_and_time(changed_time_completed)
                        return_list[-1]["completed_date"] = date + time
                        return_list[-1]["completed_date_relative"] = (
                            RFC3339_to_relative_time(
                                changed_time_completed, self._timezone
                            )
                        )

                    if return_list[-1]["parent_id"]:
                        return_list[-1]["parent_title"] = self._get_task_by_id(
                            item["id"], return_list[-1]["parent_id"]
                        )["title"]
                    else:
                        return_list[-1]["parent_title"] = None

                    if return_list[-1]["notes"]:
                        # Remove the default note from the notes
                        return_list[-1]["notes"] = return_list[-1]["notes"].replace(
                            DEFAULT_NOTE, ""
                        )

            return return_list
        else:
            return None

    def list_tasks_all(
        self,
        max_results: int = 10,
        show_completed: bool = True,
        show_deleted: bool = False,
        show_hidden: bool = False,
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
                            "last_updated_relative": None,
                            "completed_date_relative": None,
                            "due_date_relative": None,
                            "parent_title": None,
                        }
                    )

                    RFC_time_updated = task["updated"]
                    changed_time_updated = RFC3339_change_timezones(
                        RFC_time_updated, to_timezone=self._timezone
                    )
                    date, time = RFC3339_to_date_and_time(changed_time_updated)

                    return_list[-1]["last_updated"] = date + time
                    return_list[-1]["last_updated_relative"] = RFC3339_to_relative_time(
                        changed_time_updated, self._timezone
                    )

                    if return_list[-1]["due_date"]:
                        RFC_time_due = return_list[-1]["due_date"]
                        changed_time_due = RFC3339_change_timezones(
                            RFC_time_due, to_timezone=self._timezone
                        )
                        date, time = RFC3339_to_date_and_time(changed_time_due)
                        return_list[-1]["due_date"] = date + time
                        return_list[-1]["due_date_relative"] = RFC3339_to_relative_time(
                            changed_time_due, self._timezone
                        )

                    if return_list[-1]["completed_date"]:
                        RFC_time_completed = return_list[-1]["completed_date"]
                        changed_time_completed = RFC3339_change_timezones(
                            RFC_time_completed, to_timezone=self._timezone
                        )
                        date, time = RFC3339_to_date_and_time(changed_time_completed)
                        return_list[-1]["completed_date"] = date + time
                        return_list[-1]["completed_date_relative"] = (
                            RFC3339_to_relative_time(
                                changed_time_completed, self._timezone
                            )
                        )

                    if return_list[-1]["parent_id"]:
                        return_list[-1]["parent_title"] = self._get_task_by_id(
                            item["id"], return_list[-1]["parent_id"]
                        )["title"]
                    else:
                        return_list[-1]["parent_title"] = None

                    if return_list[-1]["notes"]:
                        # Remove the default note from the notes
                        return_list[-1]["notes"] = return_list[-1]["notes"].replace(
                            DEFAULT_NOTE, ""
                        )

            return return_list

        else:
            return None

    # Tasks (Get)
    ####################################################################################################
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
            logger.error(err)
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

        task_name = task_name.lower().strip()

        if tasks:
            for item in tasks:
                if item["name"].lower().strip() == task_name:
                    return_list.append(item)
            return return_list
        else:
            return None

    # Tasks (Delete)
    ####################################################################################################
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
            logger.error(err)
            return False

    def delete_tasks_by_name(self, task_name: str) -> bool:
        """
        This method deletes a task by title

        Args:
            task_name (str): The task title

        Returns:
            bool: A dictionary containing the success status or None if the task was not deleted
        """

        tasks = self.get_tasks_by_name(task_name)

        if tasks:
            responses = []
            for task in tasks:
                id = task["id"]
                list_id = task["list_id"]
                response = self._delete_task_by_id(list_id, id)
                responses.append(response)
            if all(responses):
                return {"success": True}
            else:
                return None
        else:
            return None

    # Tasks (Insert)
    ####################################################################################################
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

        body = {"title": name.strip().title()}

        if due_date:
            body["due"] = datetime_to_RFC3339(due_date)

        if notes:
            body["notes"] = notes + DEFAULT_NOTE
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

            changed_time = RFC3339_change_timezones(
                task["updated"], to_timezone=self._timezone
            )
            date, time = RFC3339_to_date_and_time(changed_time)
            return {
                "id": task["id"],
                "name": task["title"],
                "last_updated": date + time,
                "last_updated_relative": RFC3339_to_relative_time(
                    changed_time, self._timezone
                ),
            }

        except HttpError as err:
            logger.error(err)
            return None

    def insert_task_by_list_name_parent_name(
        self,
        list_name: str,
        name: str,
        due_date_year: int = 0,
        due_date_month: int = 0,
        due_date_day: int = 0,
        due_date_hour: int = 0,
        due_date_minute: int = 0,
        due_date_second: int = 0,
        notes: str = None,
        parent_name: str = None,
    ) -> dict:
        """
        This method inserts a task

        Args:
            list_name (str): The task list title
            name (str): The task title
            due_date_year (int): The task due date year (default is 0)
            due_date_month (int): The task due date month (default is 0)
            due_date_day (int): The task due date day (default is 0)
            due_date_hour (int): The task due date hour (default is 0)
            due_date_minute (int): The task due date minute (default is 0)
            due_date_second (int): The task due date second (default is 0)
            notes (str): The task notes (default is None)
            parent_name (str): The task parent title (default is None)

        Returns:
            dict: The task id, title, and updated time or None if the task was not inserted
        """

        task_lists = self.get_task_lists_by_name(list_name)
        try:
            task_list_id = task_lists[0]["id"]
        except IndexError:
            task_list_id = self.insert_task_list(list_name)["id"]
            if task_list_id == None:
                return None

        if parent_name:
            parent_tasks = self.get_tasks_by_name(parent_name)
            try:
                parent_id = parent_tasks[0]["id"]
            except IndexError:
                parent_id = None

        else:
            parent_id = None

        if due_date_year != 0 and due_date_month != 0 and due_date_day != 0:
            due_date = date_and_time_to_datetime(
                due_date_year,
                due_date_month,
                due_date_day,
                due_date_hour,
                due_date_minute,
                due_date_second,
            )

        else:
            due_date = None

        response = self._insert_task_by_list_id_parent_id(
            task_list_id, name, due_date, notes, parent_id
        )
        return {
            "id": response["id"],
            "name": response["name"],
            "last_updated": response["last_updated"],
            "last_updated_relative": response["last_updated_relative"],
        }

    # Tasks (Move)
    ####################################################################################################
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
            logger.error(err)
            return False

    # Tasks (Update)
    ####################################################################################################
    def _update_task_by_list_id_task_id(
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
        This method updates a task by id

        Args:
            list_id (str): The task list id
            task_id (str): The task id
            new_task_name (str): The new task title (default is None)
            due_date (datetime): The new task due date (default is None)
            notes (str): The new task notes (default is None)
            parent_id (str): The new task parent id (default is None)
            is_done (bool): Whether the task is done (default is None)

        Returns:
            dict: The task id, title, and updated time or None if the task was not updated
        """

        task = self._get_task_by_id(list_id, task_id)

        body = {}

        if new_task_name:
            body["title"] = new_task_name.strip().title()
        else:
            body["title"] = task["title"]

        if due_date:
            body["due"] = datetime_to_RFC3339(due_date)
        else:
            body["due"] = task.get("due", None)

        if notes:
            body["notes"] = notes + DEFAULT_NOTE
        else:
            notes = task.get("notes", None)
            if notes:
                if DEFAULT_NOTE not in notes:
                    body["notes"] = notes + DEFAULT_NOTE
                else:
                    body["notes"] = notes
            else:
                body["notes"] = DEFAULT_NOTE

        if parent_id:
            self._move_task_by_list_id_task_id_parent_id(list_id, task_id, parent_id)

        if is_done != None:
            if is_done:
                body["status"] = "completed"
                body["completed"] = datetime_to_RFC3339(
                    get_current_time(self._timezone)
                )
            else:
                body["status"] = "needsAction"
                body["completed"] = None
        else:
            body["status"] = task.get("status", None)
            body["completed"] = task.get("completed", None)

        try:
            task = (
                self._service.tasks()
                .patch(tasklist=list_id, task=task_id, body=body)
                .execute()
            )
            changed_time = RFC3339_change_timezones(
                task["updated"], to_timezone=self._timezone
            )
            date, time = RFC3339_to_date_and_time(changed_time)
            return {
                "id": task["id"],
                "name": task["title"],
                "last_updated": date + time,
                "last_updated_relative": RFC3339_to_relative_time(
                    changed_time, self._timezone
                ),
            }

        except HttpError as err:
            logger.infor.info(err)
            return None

    def update_task_by_list_name_task_name(
        self,
        list_name: str,
        task_name: str,
        new_task_name: str = None,
        due_date_year: int = 0,
        due_date_month: int = 0,
        due_date_day: int = 0,
        due_date_hour: int = 0,
        due_date_minute: int = 0,
        due_date_second: int = 0,
        notes: str = None,
        parent_name: str = None,
        is_done: bool = None,
    ) -> dict:
        """
        This method updates a task by title

        Args:
            list_name (str): The task list title
            task_name (str): The task title
            new_task_name (str): The new task title (default is None)
            due_date (str): The new task due date (default is None)
            notes (str): The new task notes (default is None)
            parent_name (str): The new task parent title (default is None)

        Returns:
            dict: The task id, title, and updated time or None if the task was not updated
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

        if due_date_year != 0 and due_date_month != 0 and due_date_day != 0:
            due_date = date_and_time_to_datetime(
                due_date_year,
                due_date_month,
                due_date_day,
                due_date_hour,
                due_date_minute,
                due_date_second,
            )
        else:
            due_date = None

        response = self._update_task_by_list_id_task_id(
            task_list_id, task_id, new_task_name, due_date, notes, parent_id, is_done
        )
        return {
            "id": response["id"],
            "name": response["name"],
            "last_updated": response["last_updated"],
            "last_updated_relative": response["last_updated_relative"],
        }

    def __call__(self, input_dict: dict):
        """
        Executes the specified action based on the input dictionary.

        Args:
            input_dict (dict): A dictionary containing the input parameters.

        Returns:
            The result of the specified action, or None if the action is invalid or incomplete.
        """
        list_all = input_dict.get("list_all_tasks", False)
        object_type = input_dict.get("object_type", None)
        list_name = input_dict.get("list_name", "My Tasks")
        task_name = input_dict.get("task_name", "My Task")
        action = input_dict.get("action", None)
        max_results = input_dict.get("max_results", 10)
        new_list_name = input_dict.get("new_list_name", "New List")
        new_task_name = input_dict.get("new_task_name", "New Task")
        due_date = input_dict.get("due_date", None)
        notes = input_dict.get("notes", None)
        parent_task_name = input_dict.get("parent_task_name", None)
        mark_as_done = input_dict.get("mark_as_done", False)

        if list_all:
            result = self.list_tasks_all(max_results)
            return result if result else {"error": "No tasks found", "level": 1}
        if object_type == None:
            return {"error": "object_type is required", "level": 2}
        if action == None:
            return {"error": "action is required", "level": 2}
        if due_date:
            year = int(due_date[0:4])
            month = int(due_date[5:7])
            day = int(due_date[8:10])
            hour = int(due_date[11:13])
            minute = int(due_date[14:16])
            second = int(due_date[17:19])
        if not due_date:
            year = month = day = hour = minute = second = 0

        if object_type == "list":
            if action == "list":
                result = self.list_task_lists_all()
                return (
                    result if result else {"error": "No task lists found", "level": 1}
                )
            elif action == "insert":
                result = self.insert_task_list(new_list_name)
                return (
                    result
                    if result
                    else {"error": "Task list not inserted", "level": 2}
                )
            elif action == "update":
                result = self.update_task_lists_by_name(list_name, new_list_name)
                return (
                    result if result else {"error": "Task list not updated", "level": 2}
                )
            elif action == "remove":
                result = self.delete_task_lists_by_name(list_name)
                return (
                    result if result else {"error": "Task list not deleted", "level": 2}
                )
            elif action == "get":
                result = self.get_task_lists_by_name(list_name)
                return (
                    result if result else {"error": "Task list not found", "level": 1}
                )

        elif object_type == "task":
            if action == "list":
                result = self.list_tasks_by_task_list_name(list_name, max_results)
                return result if result else {"error": "No tasks found", "level": 1}
            elif action == "insert":
                result = self.insert_task_by_list_name_parent_name(
                    list_name,
                    new_task_name,
                    year,
                    month,
                    day,
                    hour,
                    minute,
                    second,
                    notes,
                    parent_task_name,
                )
                return result if result else {"error": "Task not inserted", "level": 2}
            elif action == "update":
                result = self.update_task_by_list_name_task_name(
                    list_name,
                    task_name,
                    new_task_name,
                    year,
                    month,
                    day,
                    hour,
                    minute,
                    second,
                    notes,
                    parent_task_name,
                    mark_as_done,
                )
                return result if result else {"error": "Task not updated", "level": 2}
            elif action == "remove":
                result = self.delete_tasks_by_name(task_name)
                return result if result else {"error": "Task not deleted", "level": 2}
            elif action == "get":
                result = self.get_tasks_by_name(task_name)
                return result if result else {"error": "Task not found", "level": 1}

        return {"error": "Invalid action or object type", "level": 2}


if __name__ == "__main__":
    tasks_api = TasksApi(robot_id="bemo-MK1")
    tasks_api.start_mqtt()
