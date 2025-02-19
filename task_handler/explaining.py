import numpy as np
import pickle
import time
import os
from lime.lime_text import LimeTextExplainer


# Load the pipeline and labels
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(f"{CURRENT_DIR}/models/TC_Pipeline_LR_v2.pkl", "rb") as f:
    loaded_pipeline = pickle.load(f)
    
with open(f"{CURRENT_DIR}/models/labels.pkl", "rb") as f:
    labels = list(pickle.load(f))


# Define the LIME explainer
explainer = LimeTextExplainer(class_names=labels)


def tfid_word_importance(prompt: str, prediction: np.ndarray) -> tuple[dict[str, tuple[str, float]], float]:
    """
    Generate explanations for the input prompt using TF-IDF word importance.
    
    Args:
        prompt (str): The input prompt to explain.
        prediction (np.ndarray): The prediction of the input prompt.
        
    Returns:
        tuple[dict[str, tuple[str, float]], float]: A tuple containing the important words per label and the time taken to explain.
    """
    start = time.time()
    
    # Extract vectorizer and classifier components (logistic regression estimators)
    vectorizer = loaded_pipeline.named_steps['vectorizer']
    classifier_chain = loaded_pipeline.named_steps['classifier']
    log_reg_estimators = classifier_chain.estimators_
    
    # Vectorize the input prompt
    input_vectorized = vectorizer.transform([prompt]).toarray().flatten() 
    
    # Get feature names (words in the corpus used to train the model)
    feature_names = vectorizer.get_feature_names_out()
            
    # Identify important words per label
    label_word_map = {}
    
    for i, label in enumerate(labels):
        # Only for predicted labels
        if prediction[0][i] == 1:              
            # Get the weights of the logistic regression estimator for the current label
            class_weights = log_reg_estimators[i].coef_.flatten()
            
            # Get the final 1000 weights in the classifier (the weights for the model without the input of the previous models)
            class_weights = class_weights[-1000:]
            
            # Get the top 10 important words for the current label
            important_indices = np.argsort(class_weights * input_vectorized)[::-1][:10]        
            important_words = [feature_names[idx] for idx in important_indices if input_vectorized[idx] > 0]

            # Store the important words for the current label with their corresponding weights
            for word in important_words:
                if label not in label_word_map:
                    label_word_map[label] = []
                label_word_map[label].append((word, class_weights[feature_names.index(word)]))

    end = time.time()
    
    return label_word_map, end-start

def lime_explanation(prompt: str, prediction: np.ndarray) -> tuple[dict[str, tuple[str, float]], float]:
    """
    Generate explanations for the input prompt using LIME.
    
    Args:
        prompt (str): The input prompt to explain.
        prediction (np.ndarray): The prediction of the input prompt.
    
    Returns:
        tuple[dict[str, tuple[str, float]], float]: A tuple containing the important words per label and the time taken to explain.
    """
      
    start = time.time()
        
    # Get the labels to be explained
    labels_to_explain = [i for i, val in enumerate(prediction[0]) if val == 1]
    
    # Generate explanation
    exp = explainer.explain_instance(prompt, loaded_pipeline.predict_proba, num_features=10, labels=labels_to_explain)

    # Identify important words per label
    label_word_map = {}
    for label in labels_to_explain:
        label_word_map[labels[label]] = exp.as_list(label=label)
    
    end = time.time()
    
    return label_word_map, end-start


if __name__ == "__main__":
    while True:
        prompt = input("Enter a prompt, (type 'exit' to quit): ")
        if prompt == "exit":
            break
        
        # Get predictions
        start = time.time()
        new_prediction = loaded_pipeline.predict([prompt])
        predicted_labels = [labels[i] for i, val in enumerate(new_prediction[0]) if val == 1]
        end = time.time()
        
        # Get important words per task using TF-IDF word importance
        label_word_map_tfidf, time_taken_tfidf = tfid_word_importance(prompt, new_prediction)
        
        # Get important words per task using LIME
        label_word_map_lime, time_taken_lime = lime_explanation(prompt, new_prediction)

        
        # Output results
        
        print("Using TF-IDF Word Importance:")
        print("Input:", prompt)
        print("Predicted Tasks:", predicted_labels)
        print("Important Words Per Task:", label_word_map_tfidf)
        print("Time taken to predict:", end-start)
        print("Time taken to explain:", time_taken_tfidf)
        print("Time taken to predict and explain:", time_taken_tfidf + (end-start))

        print()
        
        print("Using LIME:")
        print("Input:", prompt)
        print("Predicted Tasks:", predicted_labels)
        print("Important Words Per Task:", label_word_map_lime)
        print("Time taken to predict:", end-start)
        print("Time taken to explain:", time_taken_lime)
        print("Time taken to predict and explain:", time_taken_lime + (end-start))
        
        print("*" * 50)