# %%
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, hamming_loss, f1_score
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.multioutput import ClassifierChain

import pickle
import time
import pandas as pd

# %% [markdown]
# ## Load and Preprocess Data

# %%
# Load the data
df = pd.read_csv("./datasets/bemo_prompts_dataset_v2.1.csv")

# %%
# Show 5 random rows
df.sample(5)

# %%
# Drop the first column
df.drop(df.columns[0], axis=1, inplace=True)

# %%
df.sample(5)

# %%
# Split the data into X and Y
x = df["prompt"]
Y = df.drop(columns=["prompt"])
labels = Y.columns

# %%
print(x.shape, Y.shape)

# %%
# Train-test split
x_train, x_test, Y_train, Y_test = train_test_split(
    x, Y, test_size=0.3, random_state=42, shuffle=True
)

# %% [markdown]
# ### Vanilla Classifier Chain with Logistic Regression

# %%
# Initialize the vectorizer
vectorizer = TfidfVectorizer()

# Initialize the classifier chain
classifier = ClassifierChain(LogisticRegression(), verbose=True)

# %%
# Create the pipeline

pipeline = Pipeline([("vectorizer", vectorizer), ("classifier", classifier)])

# %%
# Train the model
start = time.time()
pipeline.fit(x_train, Y_train)
end = time.time()

print(f"Training time: {end-start}")

# %%
# Predict
Y_pred = pipeline.predict(x_test)

# %%
# Evaluation
print("Accuracy:", accuracy_score(Y_test, Y_pred))
print("Hamming Loss:", hamming_loss(Y_test, Y_pred))
print("F1 Score (micro):", f1_score(Y_test, Y_pred, average="micro"))

# %%
# Test with a new example
prompt = input("Enter a prompt: ")
new_prompt = [prompt]
start = time.time()
new_prediction = pipeline.predict(new_prompt)
end = time.time()

# %%
# Get the predicted labels
predicted_labels = [labels[i] for i, val in enumerate(new_prediction[0]) if val == 1]
print("Input:", new_prompt[0])
print("Predicted Tasks:", predicted_labels)
print("Time taken:", end - start)

# %%
# Save the model
with open("./models/TC_Pipeline_LR_v3.pkl", "wb") as f:
    pickle.dump(pipeline, f)

# %%
# Save the labels
with open("./models/labels_v2.pkl", "wb") as f:
    pickle.dump(labels, f)

# %%
# Test the saved model
with open("./models/TC_Pipeline_LR_v3.pkl", "rb") as f:
    loaded_pipeline = pickle.load(f)

with open("./models/labels_v2.pkl", "rb") as f:
    labels = pickle.load(f)

new_prediction = loaded_pipeline.predict(new_prompt)
predicted_labels = [labels[i] for i, val in enumerate(new_prediction[0]) if val == 1]
print("Input:", new_prompt[0])
print("Predicted Tasks:", predicted_labels)

# %% [markdown]
# ### Vanilla Classifier Chain with XGBoost

# %%
# Initialize the vectorizer
vectorizer = TfidfVectorizer()

# Initialize the classifier chain
classifier = ClassifierChain(GradientBoostingClassifier(), verbose=True)

# %%
# Create the pipeline

pipeline = Pipeline([("vectorizer", vectorizer), ("classifier", classifier)])

# %%
# Train the model
start = time.time()
pipeline.fit(x_train, Y_train)
end = time.time()
print(f"Training time: {end-start}")

# %%
# Predict
Y_pred = pipeline.predict(x_test)

# %%
# Evaluation
print("Accuracy:", accuracy_score(Y_test, Y_pred))
print("Hamming Loss:", hamming_loss(Y_test, Y_pred))
print("F1 Score (micro):", f1_score(Y_test, Y_pred, average="micro"))

# %%
# Test with a new example
prompt = input("Enter a prompt: ")
new_prompt = [prompt]
start = time.time()
new_prediction = pipeline.predict(new_prompt)
end = time.time()

# %%
# Get the predicted labels
predicted_labels = [labels[i] for i, val in enumerate(new_prediction[0]) if val == 1]
print("Input:", new_prompt[0])
print("Predicted Tasks:", predicted_labels)
print("Time taken:", end - start)

# %%
# Save the model
with open("./models/TC_Pipeline_GB_v2.pkl", "wb") as f:
    pickle.dump(pipeline, f)

# %% [markdown]
# ### Classifier Chain with Logistic Regression and Grid Search for Hyperparameter Tuning

# %%
# Initialize the vectorizer
vectorizer = TfidfVectorizer()

# Initialize the classifier chain
classifier = ClassifierChain(LogisticRegression())

# %%
# Create the pipeline

pipeline = Pipeline([("vectorizer", vectorizer), ("classifier", classifier)])

# %%
# Define hyperparameter grid
param_grid = {
    "classifier__base_estimator__C": [0.01, 0.1, 1, 10],  # Regularization strength
    "classifier__base_estimator__penalty": [
        "l1",
        "l2",
        "elasticnet",
    ],  # Regularization type
    "classifier__base_estimator__solver": [
        "liblinear",
        "saga",
    ],  # Solver (some only support specific penalties)
    "classifier__base_estimator__max_iter": [100, 200, 500],  # Number of iterations
    "classifier__base_estimator__tol": [
        1e-4,
        1e-3,
        1e-2,
    ],  # Stopping criteria tolerance
    "classifier__base_estimator__class_weight": [
        None,
        "balanced",
    ],  # Handle imbalanced data
    "vectorizer__max_features": [100, 500, 1000],  # Number of TF-IDF features
    "vectorizer__ngram_range": [(1, 1), (1, 2)],  # Use unigrams or bigrams
}

# %%
# Initialize the grid search
grid_search = GridSearchCV(
    pipeline, param_grid, cv=3, scoring="accuracy", verbose=2, n_jobs=-1
)

# %%
# Train the model
start = time.time()
grid_search.fit(x_train, Y_train)
end = time.time()
print(f"Training time: {end-start}")

# %%
# Print best parameters and best score
print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)

# %%
# Get the best model
best_pipeline = grid_search.best_estimator_

# %%
# Predict
Y_pred = best_pipeline.predict(x_test)

# %%
# Evaluation
print("Accuracy:", accuracy_score(Y_test, Y_pred))
print("Hamming Loss:", hamming_loss(Y_test, Y_pred))
print("F1 Score (micro):", f1_score(Y_test, Y_pred, average="micro"))

# %%
# Test with a new example
prompt = input("Enter a prompt: ")
new_prompt = [prompt]
start = time.time()
new_prediction = best_pipeline.predict(new_prompt)
end = time.time()

# %%
# Get the predicted labels
predicted_labels = [labels[i] for i, val in enumerate(new_prediction[0]) if val == 1]
print("Input:", new_prompt[0])
print("Predicted Tasks:", predicted_labels)
print("Time taken:", end - start)

# %%
# Save the best model
with open("./models/TC_Pipeline_LR_v4.pkl", "wb") as f:
    pickle.dump(best_pipeline, f)
