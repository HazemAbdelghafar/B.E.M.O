import pickle
import os

import sys
from pathlib import Path

# Add the root directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils import BaseMQTTHandler

# Specify the paths to the model and labels
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MODEL_PATH = f"{CURRENT_DIR}/models/TC_Pipeline_LR_v2.pkl"
LABELS_PATH = f"{CURRENT_DIR}/models/labels.pkl"

# Define the name of the task classifier and the MQTT topics
NAME = "task_classifier"
SUB_TOPIC = "task_classifier/prompt"
PUB_TOPIC = "task_classifier/result"

class TaskClassifier(BaseMQTTHandler):
    """
    TaskClassifier is a class for classifying tasks based on a given prompt.
    """
    
    def __init__(self):
        """
        Initialize the TaskClassifier object.
        """
        
        # Initialize the BaseMQTTHandler object
        super().__init__(SUB_TOPIC, PUB_TOPIC, NAME)
        
        # Load the model and labels
        self._model = pickle.load(open(MODEL_PATH, "rb"))
        self._labels = pickle.load(open(LABELS_PATH, "rb"))
                
    def _execute_main(self, input_data: dict) -> dict:
        """
        Executes the main functionality of the class.
        
        Args:
            input_data (dict): The input data to process.
        
        Returns:
            dict: The result of the classification.
        """
        prompt = input_data["prompt"] # Get the prompt from the input data
        prediction = self._model.predict([prompt])[0] # Make a prediction using the model
        
        # Get the predicted labels based on the prediction
        predicted_labels = [self._labels[i] for i, val in enumerate(prediction) if val == 1]
        
        # Return the predicted labels
        return {"predicted_labels": predicted_labels}
        

    

if __name__ == "__main__":
    tc = TaskClassifier()
    
    # Start the MQTT client loop
    tc.client.loop_forever()



