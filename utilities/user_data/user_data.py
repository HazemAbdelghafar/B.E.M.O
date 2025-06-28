import sys
from pathlib import Path
import logging
import json
import os

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utilities import BaseMQTTHandler

DEFAULT_PATH = os.path.dirname(__file__)
DATA_JSON_FILE = os.path.join(DEFAULT_PATH, "data", "user_data.json")
DEFAULT_JSON_FILE = os.path.join(DEFAULT_PATH, "data", "default_user_data.json")
logging.basicConfig(
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    filename="./logging.log",
    encoding="utf-8",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

DEFAULT_USER_DATA = json.load(open(DEFAULT_JSON_FILE))


class UserData(BaseMQTTHandler):
    FIELDS = list(DEFAULT_USER_DATA.keys())

    def __init__(self):
        super().__init__(sub_topic="user_data/main", name="user_data")
        self.robot_id = None
        self.user_id = None
        self.user_data = {}  # Holds all user entries
        self._ensure_json_initialized()
        self._load_all_user_data()

    def execute_main(self, input_data: dict) -> dict:
        action = input_data.get("action")
        self.robot_id = input_data.get("robot_id")
        self.user_id = input_data.get("user_id")

        if not action:
            logger.error("Missing 'action' field.")
            return None
        if not self.robot_id or not self.user_id:
            logger.error("Missing 'robot_id' or 'user_id'.")
            return None

        logger.info(f"Executing action: {action}")
        logger.info(f"Robot ID: {self.robot_id}")
        logger.info(f"User ID: {self.user_id}")

        # Ensure this user exists in memory
        self._init_user_if_needed()

        if action == "get":
            key = input_data.get("key")
            if key == "all":
                return {"data": self.get_all_user_data()}
            elif key:
                if key not in self.FIELDS:
                    logger.error(f"Invalid key '{key}'")
                    return None
                return {"key": key, "value": self.get_user_data(key)}
            else:
                logger.error("Missing 'key' for get action.")
                return None

        elif action == "set":
            if "keys" in input_data and "values" in input_data:
                keys = input_data["keys"]
                values = input_data["values"]
                if not isinstance(keys, list) or not isinstance(values, list):
                    logger.error("'keys' and 'values' must be lists.")
                    return None
                if len(keys) != len(values):
                    logger.error("'keys' and 'values' must match in length.")
                    return None

                for key, value in zip(keys, values):
                    if key in self.FIELDS:
                        self.set_user_data_value(key, value)
                    else:
                        logger.warning(f"Ignored invalid key: {key}")
                self._save_all_user_data()
                return {"message": "Multiple keys updated successfully."}

            key = input_data.get("key")
            value = input_data.get("value")
            if key and value is not None:
                if key not in self.FIELDS:
                    logger.error(f"Invalid key '{key}'")
                    return None
                self.set_user_data_value(key, value)
                self._save_all_user_data()
                return {"message": f"Set {key} to {value}"}
            else:
                logger.error("Missing 'key' or 'value' for set action.")
                return None

        else:
            logger.error(f"Unknown action '{action}'")
            return None

    def _ensure_json_initialized(self):
        """Create the JSON file if it doesn't exist."""
        os.makedirs(os.path.dirname(DATA_JSON_FILE), exist_ok=True)
        if not os.path.exists(DATA_JSON_FILE) or os.stat(DATA_JSON_FILE).st_size == 0:
            with open(DATA_JSON_FILE, "w") as f:
                json.dump([], f, indent=4)
            logger.info("Initialized empty user data JSON file.")

    def _load_all_user_data(self):
        """Load the entire user data JSON into memory."""
        try:
            with open(DATA_JSON_FILE, "r") as f:
                all_entries = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load user data JSON: {e}")
            all_entries = []

        for entry in all_entries:
            rid = entry.get("robot_id")
            uid = entry.get("user_id")
            data = entry.get("user_data", {})
            if rid and uid:
                self.user_data[(rid, uid)] = {
                    key: data.get(key, "") for key in self.FIELDS
                }

    def _save_all_user_data(self):
        """Save all in-memory user data back to JSON."""
        json_entries = []
        for (rid, uid), data in self.user_data.items():
            json_entries.append(
                {
                    "robot_id": rid,
                    "user_id": uid,
                    "user_data": {key: data.get(key, "") for key in self.FIELDS},
                }
            )

        try:
            with open(DATA_JSON_FILE, "w") as f:
                json.dump(json_entries, f, indent=4)
            logger.info("User data saved to JSON.")
        except Exception as e:
            logger.error(f"Failed to save user data: {e}")

    def _init_user_if_needed(self):
        """Ensure user entry exists in memory."""
        key = (self.robot_id, self.user_id)
        if key not in self.user_data:
            logger.info(f"Initializing new user entry for {key}")
            self.user_data[key] = {field: "" for field in self.FIELDS}

    def get_user_data(self, key: str) -> str:
        return self.user_data.get((self.robot_id, self.user_id), {}).get(key, "")

    def set_user_data_value(self, key: str, value: str):
        self.user_data[(self.robot_id, self.user_id)][key] = value

    def get_all_user_data(self) -> dict:
        """
        Return all user data. If all fields are empty, fallback to default values.
        """
        data = self.user_data.get((self.robot_id, self.user_id), {})
        if all(data.get(field, "") == "" for field in self.FIELDS):
            if self.robot_id == "bemo-MK1" and self.user_id == "user-MK1":
                logger.info(
                    f"Returning DEFAULT_USER_DATA for {self.robot_id}, {self.user_id}"
                )
                return DEFAULT_USER_DATA.copy()
            else:
                logger.info(
                    f"Returning empty user data for {self.robot_id}, {self.user_id}"
                )
                return {}
        return {key: data.get(key, "") for key in self.FIELDS}

    def set_user_data(self, data: dict):
        self.user_data[(self.robot_id, self.user_id)] = {
            key: data[key] for key in self.FIELDS if key in data
        }


if __name__ == "__main__":
    user_data_module = UserData()
    user_data_module.start_mqtt()
