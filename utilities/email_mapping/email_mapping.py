DEFAULT_MAPPING = {
    "mohamed.y.abdelnasser@gmail.com": "mohamed abdelnasser",
    "begadtamim.a@gmail.com": "begad tamim",
    "hazem.metwalli23@gmail.com": "hazem abdelghafar",
    "abdosaaed749@gmail.com": "abdelrahman saeed",
    "mohamedelfeel62@gmail.com": "mohamed abdelraheem",
    "youssefaymanmohamed1@gmail.com": "youssef ayman",
    "abouelfarag@aast.edu": "dr. ahmed abouelfarag",
    "omar.o.shalash@aast.edu": "dr. omar shalash",
    "hanysaid2000@aast.edu": "dr. hany hanafy",
    "yhanafy@aast.edu": "dr. yasser hanafy",
    "obadawy2@gmail.com": "dr. ossama badawy",
    "ahshaer@alexu.edu.eg": "dr. ahmed shaer",
    "prof.mail.metwalli@gmail.com": "eng. ahmed metwalli",
    "osamahesham357@gmail.com": "eng. osama hesham",
}


class EmailMapping:
    """
    A class to handle the mapping of email addresses to their corresponding devices.
    """

    def __init__(self, mapping: dict = DEFAULT_MAPPING):
        """
        Initialize the EmailMapping object with a default mapping.

        Args:
            mapping (dict): A dictionary mapping email addresses to device names.
        """
        self.__mapping = mapping

    def get_name(self, email_address: str) -> str:
        """
        Get the name corresponding to an email address.

        Args:
            email_address (str): The email address to get the name for.

        Returns:
            str: The name of the email address.
        """
        return self.__mapping.get(email_address, "Unknown Email")

    def get_email_address(self, name: str) -> str:
        """
        Get the email address corresponding to a name.
        """
        name = name.lower()
        for email, name_ in self.__mapping.items():
            if name == name_:
                return email
        return "Unknown Name"

    def add_mapping(self, email_address: str, name: str):
        """
        Add a new mapping to the dictionary.

        Args:
            email_address (str): The email address to add.
            name (str): The name of the email address.
        """
        self.__mapping[email_address] = name

    def remove_mapping_based_on_email(self, email_address: str):
        """
        Remove a mapping from the dictionary.

        Args:
            email_address (str): The email address to remove.
        """
        if email_address in self.__mapping:
            del self.__mapping[email_address]
        else:
            print(f"Email '{email_address}' not found in mapping.")

    def remove_mapping_based_on_name(self, name: str):
        """
        Remove a mapping from the dictionary.

        Args:
            name (str): The name of the email address to remove.
        """
        name = name.lower()
        for email, name_ in self.__mapping.items():
            if name == name_:
                del self.__mapping[email]
                return
        print(f"Name '{name}' not found in mapping.")

    def update_mapping(self, email_address: str, name: str):
        """
        Update an existing mapping in the dictionary.

        Args:
            email_address (str): The email address to update.
            name (str): The new name of the email address.
        """
        if email_address in self.__mapping:
            self.__mapping[email_address] = name
        else:
            print(f"Email '{email_address}' not found in mapping.")

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
            mapping (dict): A new dictionary of email-name mappings.
        """
        self.__mapping = mapping

    def __str__(self):
        """
        String representation of the EmailMapping object.

        Returns:
            str: A string representation of the mapping.
        """
        return str(self.__mapping)


# Example usage
if __name__ == "__main__":
    email_mapping = EmailMapping()

    print(email_mapping.get_name("mohamed.y.abdelnasser@gmail`.com"))
    print(email_mapping.get_email_address("Begad Tamim"))
