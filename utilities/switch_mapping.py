DEFAULT_MAPPING = {
    "switch_1": "living room lights",
    "switch_2": "fan",
    "switch_3": "television",
    "switch_4": "air conditioner",
    "switch_5": "speaker",
}


class SwitchMapping:
    """
    A class to handle the mapping of switch names to their corresponding devices.
    """

    def __init__(self, mapping: dict = DEFAULT_MAPPING):
        """
        Initialize the SwitchMapping object with a default mapping.

        Args:
            mapping (dict): A dictionary mapping switch names to device names.
        """
        self.__mapping = mapping

    def get_device_name(self, switch_name: str) -> str:
        """
        Get the device name corresponding to a switch name.

        Args:
            switch_name (str): The name of the switch.

        Returns:
            str: The name of the device.
        """
        return self.__mapping.get(switch_name, "Unknown Device")

    def add_mapping(self, switch_name: str, device_name: str):
        """
        Add a new mapping to the dictionary.

        Args:
            switch_name (str): The name of the switch.
            device_name (str): The name of the device.
        """
        self.__mapping[switch_name] = device_name

    def remove_mapping(self, switch_name: str):
        """
        Remove a mapping from the dictionary.

        Args:
            switch_name (str): The name of the switch to remove.
        """
        if switch_name in self.__mapping:
            del self.__mapping[switch_name]
        else:
            print(f"Switch '{switch_name}' not found in mapping.")

    def update_mapping(self, switch_name: str, device_name: str):
        """
        Update an existing mapping in the dictionary.

        Args:
            switch_name (str): The name of the switch.
            device_name (str): The new name of the device.
        """
        if switch_name in self.__mapping:
            self.__mapping[switch_name] = device_name
        else:
            print(f"Switch '{switch_name}' not found in mapping.")

    def get_all_mappings(self) -> dict:
        """
        Get all mappings in the dictionary.

        Returns:
            dict: A dictionary of all switch-device mappings.
        """
        return self.__mapping

    def set_mapping(self, mapping: dict):
        """
        Set the mapping to a new dictionary.

        Args:
            mapping (dict): A new dictionary of switch-device mappings.
        """
        self.__mapping = mapping

    def __str__(self):
        """
        String representation of the SwitchMapping object.

        Returns:
            str: A string representation of the mapping.
        """
        return str(self.__mapping)


# Example usage
if __name__ == "__main__":
    switch_mapping = SwitchMapping()

    # Get device name for a switch
    print(switch_mapping.get_device_name("switch_1"))  # Output: living room lights

    # Add a new mapping
    switch_mapping.add_mapping("switch_6", "door lock")

    # Update an existing mapping
    switch_mapping.update_mapping("switch_2", "ceiling fan")

    # Remove a mapping
    switch_mapping.remove_mapping("switch_3")

    # Get all mappings
    print(
        switch_mapping.get_all_mappings()
    )  # Output: {'switch_1': 'living room lights', ...}

    # Set a new mapping
    switch_mapping.set_mapping({"switch_7": "window"})

    # Print the mapping
    print(switch_mapping)  # Output: {'switch_7': 'window'}
