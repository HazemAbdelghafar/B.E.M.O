from datetime import datetime
import os
import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .init_user import init_user
from .utils import (
    RFC3339_to_date_and_time,
    datetime_to_RFC3339,
    RFC3339_to_relative_time,
    RFC3339_change_timezones,
    date_and_time_to_datetime,
    get_current_time,
)

from pprint import pprint


DEFAULT_NOTE = "\n\nB.E.M.O"
DEFAULT_PATH = os.path.dirname(__file__)
DEFAULT_TIMEZONE = "Africa/Cairo"


class TasksApi:
    def __init__(self, user_id: str, timezone: str = DEFAULT_TIMEZONE) -> None:
        """
        This method initializes the tasks API

        Args:
            user_id (str): The user id
            timezone (str): The timezone (default is Africa/Cairo)

        Returns:
            None
        """

        self._creds = init_user(user_id)
        self._service = build("tasks", "v1", credentials=self._creds)
        self._timezone = timezone

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
            print(err)
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

        name = name.lower().strip()

        if task_lists:
            for item in task_lists:
                if item["name"].lower().strip() == name:
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
            print(err)
            return None, None, None

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
            print(err)
            return None, None, None

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
            print(err)
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
            print(err)
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
            print(err)
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
        }

    def __call__(self, input_dict: dict):
        """
        Executes the specified action based on the input dictionary.

        Args:
            input_dict (dict): A dictionary containing the input parameters.

        Returns:
            The result of the specified action, or None if the action is invalid or incomplete.
        """
        object_type = input_dict.get("list_or_task", None)
        list_name = input_dict.get("list_name", None)
        task_name = input_dict.get("task_name", None)
        action = input_dict.get("action", None)
        max_results = input_dict.get("max_output", 10)
        list_all = input_dict.get("list_all_tasks", False)
        new_list_name = input_dict.get("new_list_name", None)
        new_task_name = input_dict.get("new_task_name", None)
        due_date = input_dict.get("due_date", None)
        notes = input_dict.get("notes", None)
        parent_task_name = input_dict.get("parent_task", None)
        mark_done = input_dict.get("mark_as_done", False)

        if list_all and not object_type and not list_name and not action:
            return self.list_tasks_all(max_results)

        if not object_type or not list_name or not action:
            return None

        if object_type == "list":
            if action == "list":
                if list_all:
                    return self.list_task_lists_all(max_results)
                else:
                    return self.get_task_lists_by_name(list_name)
            elif action == "insert":
                return self.insert_task_list(list_name)
            elif action == "update":
                if not new_list_name:
                    return None
                return self.update_task_lists_by_name(list_name, new_list_name)
            elif action == "remove":
                return self.delete_task_lists_by_name(list_name)
            elif action == "get":
                return self.get_task_lists_by_name(list_name)

        elif object_type == "task":
            if due_date:
                year = int(due_date[0:4])
                month = int(due_date[5:7])
                day = int(due_date[8:10])
                hour = int(due_date[11:13])
                minute = int(due_date[14:16])
                second = int(due_date[17:19])
            if not due_date:
                year = month = day = hour = minute = second = 0
            if action == "list":
                if list_all:
                    return self.list_tasks_all(max_results)
                else:
                    return self.list_tasks_by_task_list_name(list_name, max_results)
            elif action == "insert":
                if not task_name:
                    return None
                return self.insert_task_by_list_name_parent_name(
                    list_name,
                    task_name,
                    year,
                    month,
                    day,
                    hour,
                    minute,
                    second,
                    notes,
                    parent_task_name,
                )
            elif action == "update":
                if not task_name:
                    return None
                return self.update_task_by_list_name_task_name(
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
                    mark_done,
                )
            elif action == "remove":
                if not task_name:
                    print("No task name provided.")
                    return None
                return self.delete_tasks_by_name(task_name)
            elif action == "get":
                if not task_name:
                    return None
                return self.get_tasks_by_name(task_name)

        return None

if __name__ == "__main__":
    
    # Initialize the tasks API
    tasks_api = TasksApi("0")

    input_dict_list = [
        # {
        #     "method": "todo",
        #     "list_or_task": "task",
        #     "list_name": "my tasks",
        #     "action": "list",
        #     "list_all_tasks": False,
        # },
        {
            "method": "todo",
            "list_all_tasks": True,
        },
        # {
        #     "method": "todo",
        #     "list_or_task": "task",
        #     "list_name": "my tasks",
        #     "task_name": "DEPI",
        #     "action": "insert",
        #     "due_date": "2025-01-05T21:49:36",
        # },
        # {
        #     "method": "todo",
        #     "list_or_task": "task",
        #     "list_name": "my tasks",
        #     "task_name": "DEPI",
        #     "action": "remove",
        # },
        # {
        #     "method": "todo",
        #     "list_or_task": "task",
        #     "list_name": "my tasks",
        #     "task_name": "Hi",
        #     "action": "update",
        #     "new_task_name": "meeting",
        # },
        # {
        #     "method": "todo",
        #     "list_or_task": "list",
        #     "list_name": "test list",
        #     "action": "update",
        #     "new_list_name": "iSchool",
        # },
    ]

    for input_dict in input_dict_list:
        pprint(tasks_api(input_dict))
        print("\n")


# if __name__ == "__main__":

#     new_list_name = "TEST lisT"
#     updated_list_name = "NEW TEST LIST"

#     # Initialize the tasks API
#     tasks_api = TasksApi("1")

#     print("Task Lists:")
#     task_lists = tasks_api.list_task_lists_all()

#     with open(DEFAULT_PATH + "/test/task_lists.json", "w") as f:
#         json.dump(task_lists, f, indent=4)
#     print(f"Task Lists saved to {DEFAULT_PATH + '/test/task_lists.json'}")

#     # if task_lists:
#     #     for item in task_lists:
#     #         print(f"{item['name']} ({item['id']}) {item['last_updated']}")

#     # else:
#     #     print("No task lists found.")

#     # print("Task List by Title (My Tasks):")
#     # task_lists = tasks_api.get_task_lists_by_name("My Tasks")
#     # for item in task_lists:
#     #     print(f"{item['name']} ({item['id']}) {item['last_updated']}")

#     # print(f"Inserting Task List ({new_list_name})...")
#     # task_list = tasks_api.insert_task_list(new_list_name)
#     # print(f"{task_list['name']} ({task_list['id']}) {task_list['last_updated']}")

#     # print(f"Update Task List ({updated_list_name})...")
#     # task_lists = tasks_api.update_task_lists_by_name(new_list_name, updated_list_name)
#     # for item in task_lists:
#     #     print(f"{item['name']} ({item['id']}) {item['last_updated']}")

#     # print(f"Delete Task List ({updated_list_name})...")
#     # result = tasks_api.delete_task_lists_by_name(updated_list_name)
#     # if result:
#     #     print(f"Task List ({updated_list_name}) was deleted.")
#     # else:
#     #     print(f"Task List ({updated_list_name}) was not deleted.")

#     # print("Task Lists after deletion:")
#     # task_lists = tasks_api.list_task_lists_all()

#     # if task_lists:
#     #     for item in task_lists:
#     #         print(f"{item['name']} ({item['id']}) {item['last_updated']}")

#     # else:
#     #     print("No task lists found.")

#     print("Tasks")
#     tasks = tasks_api.list_tasks_all()

#     with open(DEFAULT_PATH + "/test/tasks.json", "w") as f:
#         json.dump(tasks, f, indent=4)
#     print(f"Tasks saved to {DEFAULT_PATH + '/test/tasks.json'}")

#     # if tasks:
#     #     print("Tasks:")
#     #     pprint(tasks)
#     # else:
#     #     print("No tasks found.")

#     # print("Task by Name (Test 1):")
#     # task = tasks_api.get_tasks_by_name("Test 1")

#     # if task:
#     #     pprint(task)
#     # else:
#     #     print("No task found.")

#     # print(f"Delete Task (Test)...")
#     # result = tasks_api.delete_tasks_by_name("Test")

#     # if result:
#     #     print(f"Task (Test) was deleted.")
#     # else:
#     #     print(f"Task (Test) was not deleted.")

#     print("Insert Task (Test 1)...")
#     tasks = tasks_api.insert_task_by_list_name_parent_name(
#         new_list_name,
#         "Test 1",
#         2024,
#         11,
#         30,
#         0,
#         0,
#         0,
#         "Test 1 Notes",
#     )

#     # if tasks:
#     #     print(f"{tasks['name']} ({tasks['id']}) {tasks['last_updated']}")
#     # else:
#     #     print("Task (Test 3) was not inserted.")

#     # print("Move Task (Test 3) under Test 1...")
#     # result = tasks_api.move_task_by_list_name_task_name_parent_name(
#     #     "New Test List",
#     #     "Test 3",
#     #     parent_name="Test 1",
#     # )
#     # if result:
#     #     print(f"Task (Test 3) was moved.")
#     # else:
#     #     print(f"Task (Test 3) was not moved.")

#     # print("Move Task (Test 3) from New Test List to Test List...")
#     # result = tasks_api.move_task_by_list_name_task_name_parent_name(
#     #     "New Test List",
#     #     "Test 3",
#     #     new_list_name="My Tasks",
#     # )
#     # if result:
#     #     print(f"Task (Test 3) was moved.")
#     # else:
#     #     print(f"Task (Test 3) was not moved.")

#     print("Update Task (Test 1)...")
#     task = tasks_api.update_task_by_list_name_task_name(
#         new_list_name,
#         "Test 1",
#         new_task_name="Test 1 Updated",
#         notes="Test 1 Updated Notes",
#     )
#     # if task:
#     #     print(f"{task['name']} ({task['id']}) {task['last_updated']}")
#     # else:
#     #     print("Task (Test 3) was not updated.")
