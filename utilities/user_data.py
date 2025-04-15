
# TODO: Add more user data, This is a placeholder, update with actual user data with its own file
# TODO: Add it in the prompt inputs langchain
DEFAULT_USER_DATA = {
    "location": "Cairo, Egypt",
    "timezone": "Africa/Cairo",
    "name": "Ali Mohamed Abdelnasser",
    "job_title": "Software Engineer",
    "age": "18"
}

class UserData:
    """
    UserData is a class for handling user data.
    """
    
    def __init__(self, user_data: dict = DEFAULT_USER_DATA):
        """
        Initialize the UserData object with default user data.
        
        Args:
            user_data (dict): A dictionary containing user data.
        """
        self.user_data = user_data
    
    def get_user_data(self, key: str) -> str:
        """
        Get the value of a specific key in the user data.
        
        Args:
            key (str): The key to retrieve the value for.
        
        Returns:
            str: The value associated with the key.
        """
        return self.user_data.get(key, "")
    
    def add_user_data(self, key: str, value: str):
        """
        Add a new key-value pair to the user data.
        
        Args:
            key (str): The key to add.
            value (str): The value to associate with the key.
        """
        self.user_data[key] = value
        
    def remove_user_data(self, key: str):
        """
        Remove a key-value pair from the user data.
        Args:
            key (str): The key to remove.
        """
        if key in self.user_data:
            del self.user_data[key]
        else:
            print(f"Key '{key}' not found in user data.")
            
    def update_user_data(self, key: str, value: str):
        """
        Update the value of a specific key in the user data.
        
        Args:
            key (str): The key to update.
            value (str): The new value to associate with the key.
        """
        if key in self.user_data:
            self.user_data[key] = value
        else:
            print(f"Key '{key}' not found in user data.")
            
    def get_all_user_data(self) -> dict:
        """
        Get all user data.
        
        Returns:
            dict: A dictionary containing all user data.
        """
        return self.user_data
    
    def set_user_data(self, user_data: dict):
        """
        Set the user data to a new dictionary.
        
        Args:
            user_data (dict): A dictionary containing user data.
        """
        self.user_data = user_data
        
    def __str__(self):
        """
        Get a string representation of the user data.
        
        Returns:
            str: A string representation of the user data.
        """
        return str(self.user_data)
    
# Example usage
if __name__ == "__main__":
    user_data = UserData()
    
    # Get user data
    print(user_data.get_user_data("name"))  # Output: Ali Mohamed Abdelnasser
    
    # Add user data
    user_data.add_user_data("age", "30")
    print(user_data.get_all_user_data())  # Output: {'location': 'Cairo, Egypt', 'timezone': 'Africa/Cairo', 'name': 'Ali Mohamed Abdelnasser', 'job_title': 'Software Engineer', 'age': '30'}
    
    # Update user data
    user_data.update_user_data("age", "31")
    print(user_data.get_all_user_data())  # Output: {'location': 'Cairo, Egypt', 'timezone': 'Africa/Cairo', 'name': 'Ali Mohamed Abdelnasser', 'job_title': 'Software Engineer', 'age': '31'}
    
    # Remove user data
    user_data.remove_user_data("age")
    print(user_data.get_all_user_data())  # Output: {'location': 'Cairo, Egypt', 'timezone': 'Africa/Cairo', 'name': 'Ali Mohamed Abdelnasser', 'job_title': 'Software Engineer'}
    
    # Set user data
    user_data.set_user_data({"location": "New York, USA", "timezone": "America/New_York"})
    
    print(user_data.get_all_user_data())  # Output: {'location': 'New York, USA', 'timezone': 'America/New_York'}
    
    # String representation
    print(user_data)  # Output: {'location': 'New York, USA', 'timezone': 'America/New_York'}
    