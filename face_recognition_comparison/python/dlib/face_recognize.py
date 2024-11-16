import face_recognition
import cv2
import pickle
import sys
import numpy as np
import json

# Path to the known encodings file
encoding_file_path = "/home/samsepi0l/Project/opencvpy/known_face_encodings.pkl"

# Check for input arguments
if len(sys.argv) < 2:
    print("Usage: python recognize_faces.py <test_image_path>")
    exit()

test_image_path = sys.argv[1]

# Function to write results to a JSON file
def write_json(result, output_file="output.json"):
    data = {"recognized": result}
    with open(output_file, "w") as f:
        json.dump(data, f)
    print(f"Result written to {output_file}: {data}")

print("Running recognition script...")

try:
    # Load the known encodings
    print(f"Loading encodings from {encoding_file_path}")
    with open(encoding_file_path, 'rb') as f:
        known_face_encodings, known_face_names = pickle.load(f)
        print("Encodings loaded successfully.")

    # Load the test image
    print(f"Processing test image: {test_image_path}")
    test_image = face_recognition.load_image_file(test_image_path)

    if test_image is None:
        print("Error: Test image not found or failed to load.")
        write_json(0)  # Output 0 if the image is not found
        exit()

    # Detect faces and compute encodings in the test image
    test_face_locations = face_recognition.face_locations(test_image)
    test_face_encodings = face_recognition.face_encodings(test_image, test_face_locations)

    if not test_face_encodings:
        print("No faces found in the test image.")
        write_json(0)  # Output 0 if no faces are found
        exit()

    # Recognize faces in the test image
    print("Recognizing faces in the test image...")
    recognized = 0  # Default to 0 (no match found)

    for face_encoding in test_face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            recognized = 1  # Match found
            break  # Stop further checks once a match is found

    # Write the result to a JSON file
    write_json(recognized)

except Exception as e:
    print(f"Error: {e}")
    write_json(0)  

