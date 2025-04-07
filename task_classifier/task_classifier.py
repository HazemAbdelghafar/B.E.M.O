import pickle
import os
import string

import sys
from pathlib import Path

# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils import BaseMQTTHandler

# Specify the paths to the model and labels
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MODEL_PATH = f"{CURRENT_DIR}/models/TC_Pipeline_LR_v2.pkl"
LABELS_PATH = f"{CURRENT_DIR}/models/labels.pkl"

# Define the name of the module and the topics
NAME = "task_classifier"
SUB_TOPIC = "task_classifier/prompt"

# TODO: Add learning resources
class TaskClassifier(BaseMQTTHandler):
    """
    TaskClassifier is a class for classifying tasks based on a given prompt.
    """
    
    def __init__(self):
        """
        Initialize the TaskClassifier object.
        """
        
        # Initialize the BaseMQTTHandler object
        super().__init__(SUB_TOPIC, NAME)
        
        # Load the model and labels
        self.__model = pickle.load(open(MODEL_PATH, "rb"))
        self.__labels = pickle.load(open(LABELS_PATH, "rb"))
        self._bemo_strings = [
            "bemo", "bmo", "bimo", "vemo", "vimo", "vmo", 
            "nemo", "kemo", "bbmo", "moo", "bemoo", "bemu", 
            "beemo", "temo"
        ]

        
    def execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.
        
        Args:
            input_data (dict): The input data to process.
        
        Returns:
            dict: The result of the classification.
        """
        prompt = input_data["prompt"] # Get the prompt from the input data
        prompt = self.preprocess_prompt(prompt) # Preprocess the prompt
        prediction = self.__model.predict([prompt])[0] # Make a prediction using the model
        
        # Get the predicted labels based on the prediction
        predicted_labels = [self.__labels[i] for i, val in enumerate(prediction) if val == 1]
        
        # Return the predicted labels
        return {"predicted_labels": predicted_labels, "preprocessed_prompt": prompt}
        
    def preprocess_prompt(self, prompt: str) -> str:
        """
        Preprocess the prompt for classification.
        
        Args:
            prompt (str): The prompt to preprocess.
        
        Returns:
            str: The preprocessed prompt.
        """
        
        # Remove punctuation
        prompt = prompt.translate(str.maketrans('', '', string.punctuation))
        
        # Lowercase
        prompt = prompt.lower()
        
        # Remove bemo strings and all preceding words
        for bemo_string in self._bemo_strings:
            if bemo_string in prompt:
                prompt = prompt.split(bemo_string)[1]
                
        # Remove extra spaces
        prompt = " ".join(prompt.split())
        
        return prompt
            
if __name__ == "__main__":
    tc = TaskClassifier()
    
    # Start the MQTT client loop
    tc.start()



