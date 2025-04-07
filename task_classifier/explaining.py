import numpy as np
import pickle
import time
import os
from lime.lime_text import LimeTextExplainer
from pprint import pprint
import string

# Load the pipeline and labels
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

with open(f"{CURRENT_DIR}/models/TC_Pipeline_LR_v2.pkl", "rb") as f:
    loaded_pipeline = pickle.load(f)
    
with open(f"{CURRENT_DIR}/models/labels.pkl", "rb") as f:
    labels = list(pickle.load(f))

bemo_strings = [
    "bemo", "bmo", "bimo", "vemo", "vimo", "vmo", 
    "nemo", "kemo", "bbmo", "moo", "bemoo", "bemu", 
    "beemo", "temo"
]

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
                label_word_map[label].append((word, class_weights[np.where(feature_names == word)[0][0]]))

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

#! Not Working and i will Not fix it
def split_prompt(prompt: str, label_word_map: dict[str, tuple[str, float]]) -> list[str]:
    """
    Split the input prompt into multiple prompts, based on the label words map.
    
    Args:
        prompt (str): The input prompt to split.
        label_word_map (dict[str, tuple[str, float]]): The important words per label.
        
    Returns:
        list[str]: A list of prompts, split based on the important words per label.
    """
    number_of_splits = len(label_word_map)
    print("Number of splits:", number_of_splits)

    # Filter out words with low weights
    THRESHOLD = 0.109
    for label, words in label_word_map.items():
        label_word_map[label] = [(word, weight) for word, weight in words if weight > THRESHOLD]
    
    words = prompt.split()
    
    # Split the prompt to number of splits as equal as possible
    new_prompts = []
    length_of_split = len(prompt.split()) // number_of_splits
    chunks = [words[i:i+length_of_split] for i in range(0, len(words), length_of_split)]

    if len(chunks) > number_of_splits:
        chunks[-2] += chunks[-1]
        chunks.pop()
    
    print("Label Word Map:") 
    pprint(label_word_map)
    
    print("Chunks:")
    print(chunks)
    
    # Provide each chunk with a label score
    scores = [{} for _ in range(len(chunks))]
    for i, chunk in enumerate(chunks):
        for label, words in label_word_map.items():
            scores[i][label] = 0
            for word, weight in words:
                if word in chunk:
                    scores[i][label] += weight
                                
    print("Scores:")
    pprint(scores)
            
    # Assign each chunk to a label based on the highest score while keeping the order of the chunks
    assigned_chunks = []
    for i, chunk in enumerate(chunks):
        assigned_label = max(scores[i], key=scores[i].get)
        assigned_chunks.append((assigned_label, chunk))
                
    print("Assigned Chunks:")
    pprint(assigned_chunks)    
    
    # Get the words that exist in the wrong chunks based on the assigned labels and the label word map
    wrong_words = []
    for label, words in label_word_map.items():
        for word, weight in words:
            for assigned_label, chunk in assigned_chunks:
                if assigned_label != label and word in chunk:
                    wrong_words.append(word)
                
    print("Wrong Words:")
    print(wrong_words)
    
    wrongs_words_indices = []
    for word in wrong_words:
        for i, chunk in enumerate(chunks):
            if word in chunk:
                wrongs_words_indices.append((i, chunk.index(word)))
                
    print("Wrong Words Indices:")
    print(wrongs_words_indices)
    
    # Check if the wrong words will be moved back or forward
    for i, j in wrongs_words_indices:
        chunk_length = len(chunks[i])
        if j < chunk_length // 2:
            # Move the word and all words before it to the previous chunk
            chunks[i-1] += chunks[i][:j+1]
            # Remove the word from the current chunk
            chunks[i] = chunks[i][j+1:]
        else:
            # Move the word and all words after it to the next chunk
            chunks[i+1] = chunks[i][j:] + chunks[i+1]
            # Remove the word from the current chunk
            chunks[i] = chunks[i][:j]
            
        
    print("Chunks After Moving Wrong Words:")
    print(chunks)
    
    for chunk in chunks:
        print("Chunk Length:", len(chunk))
        new_prompts.append(" ".join(chunk))

    
                
    return new_prompts

def preprocess_prompt(prompt: str) -> str:
    """
    Preprocess the input prompt.
    
    Args:
        prompt (str): The input prompt to preprocess.
        
    Returns:
        str: The preprocessed prompt.
    """
    # Remove punctuation
    prompt = prompt.translate(str.maketrans('', '', string.punctuation))
    
    # Lowercase
    prompt = prompt.lower()
    
    # Remove bemo strings and all preceding words
    for bemo_string in bemo_strings:
        if bemo_string in prompt:
            prompt = prompt.split(bemo_string)[1]
            
    # Remove extra spaces
    prompt = " ".join(prompt.split())
    
    return prompt

# if __name__ == "__main__":
#     while True:
#         prompt = input("Enter a prompt, (type 'exit' to quit): ")
#         if prompt == "exit":
#             break
        
#         # Get predictions
#         start = time.time()
#         new_prediction = loaded_pipeline.predict([prompt])
#         predicted_labels = [labels[i] for i, val in enumerate(new_prediction[0]) if val == 1]
#         end = time.time()
        
#         # # Get important words per task using TF-IDF word importance
#         # label_word_map_tfidf, time_taken_tfidf = tfid_word_importance(prompt, new_prediction)
        
#         # Get important words per task using LIME
#         label_word_map_lime, time_taken_lime = lime_explanation(prompt, new_prediction)

        
#         # Output results
        
#         # print("Using TF-IDF Word Importance:")
#         # print("Input:", prompt)
#         # print("Predicted Tasks:", predicted_labels)
#         # print("Important Words Per Task:")
#         # pprint(label_word_map_tfidf)
#         # print("Time taken to predict:", end-start)
#         # print("Time taken to explain:", time_taken_tfidf)
#         # print("Time taken to predict and explain:", time_taken_tfidf + (end-start))

#         # print()
        
#         print("Using LIME:")
    
#         print("Input:", prompt)
#         # print("Predicted Tasks:", predicted_labels)
#         # print("Important Words Per Task:")
#         pprint(label_word_map_lime)
#         # print("Time taken to predict:", end-start)
#         # print("Time taken to explain:", time_taken_lime)
#         # print("Time taken to predict and explain:", time_taken_lime + (end-start))
        
#         print(split_prompt(prompt, label_word_map_lime))
        
#         print("*" * 50)

if __name__ == "__main__":    
    test_prompts = [
        "Hey Bemo, play some relaxing music, then schedule a doctor appointment and email my client.", # smart home, todo, mail
        "Hey Bemo, remind me that I have a meeting at 5 pm and send an email to Dr Ali.",  #todo, mail
        "Hey Bemo, remind me to water the plants at 7 am and email my assistant about today's schedule.",  #todo, mail
        "Hey Bemo, turn off the kitchen lights and remind me to pay the electricity bill at 5 pm.",  # smart home, todo
        "Hey Bemo, send an email to my professor regarding my thesis and turn on the study room lamp.",  # mail, smart home
        "Hey Bemo, what's the news today and open the living room blinds?",  # general questions, smart home
        "Hey Bemo, remind me to take my medication at 9 pm and send an email to my doctor.",  #todo, mail
        "Hey Bemo, what time is my next meeting and lock the front door.",  # general questions, smart home
        "Hey Bemo, email my manager about the deadline extension and remind me to submit the report by noon.",  # mail, todo
        "Hey Bemo, turn off the heater and what's today's temperature?",  # smart home, general questions
        "Hey Bemo, remind me to call Dad at 6 pm, email him about the family gathering, and check what day it is today.",  #todo, mail, general questions
        "Hey Bemo, set a reminder for my flight at 10 am, email my assistant the itinerary, check the weather, and turn on the porch light.",  #todo, mail, general questions, smart home
    ]
    
    
    for i, prompt in enumerate(test_prompts):
        print("Test Prompt", i+1)
        preprocessed_prompt = preprocess_prompt(prompt)
        
        # Get predictions
        start = time.time()
        new_prediction = loaded_pipeline.predict([preprocessed_prompt])
        predicted_labels = [labels[i] for i, val in enumerate(new_prediction[0]) if val == 1]
        end = time.time()
        
        # # Get important words per task using TF-IDF word importance
        # label_word_map_tfidf, time_taken_tfidf = tfid_word_importance(prompt, new_prediction)
        
        # Get important words per task using LIME
        label_word_map_lime, time_taken_lime = lime_explanation(preprocessed_prompt, new_prediction)


        print("Prompt:", prompt)
        print("Input:", preprocessed_prompt)
        # print("Predicted Tasks:", predicted_labels)
        # print("Important Words Per Task:")
        # pprint(label_word_map_lime)
        # print("Time taken to predict:", end-start)
        # print("Time taken to explain:", time_taken_lime)
        # print("Time taken to predict and explain:", time_taken_lime + (end-start))
        
        print(split_prompt(preprocessed_prompt, label_word_map_lime))
        
        print("*" * 50)