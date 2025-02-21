import pickle
import time
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MODEL_PATH = f"{CURRENT_DIR}/models/TC_Pipeline_LR_v2.pkl"
LABELS_PATH = f"{CURRENT_DIR}/models/labels.pkl"


class TaskClassifier:
    def __init__(self):
        self.model = pickle.load(open(MODEL_PATH, 'rb'))
        self.labels = list(pickle.load(open(LABELS_PATH, 'rb')))
                
    def __call__(self, prompt):
        start = time.time()
        prediction = self.model.predict([prompt])
        tasks = [self.labels[i] for i, val in enumerate(prediction[0]) if val == 1]
        end = time.time()
        
        return tasks, end-start
    

def main():
    tc = TaskClassifier()
    print(tc("Hey Bemo, play some relaxing music, then schedule a doctor appointment and email my client."))

if __name__ == "__main__":
    main()        



