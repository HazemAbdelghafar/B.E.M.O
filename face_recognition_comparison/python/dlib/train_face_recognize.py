import face_recognition
import cv2
import pickle
import sys

# Default encoding file path
DEFAULT_ENCODING_FILE_PATH = "/home/samsepi0l/Project/opencvpy/known_face_encodings.pkl"

def main(train_image_path):
    print("Running training script...")

    try:
        # Load and encode the training image
        print(f"Processing training image: {train_image_path}")
        train_image = cv2.imread(train_image_path)

        if train_image is None:
            print("Error: Training image not found or failed to load.")
            exit()

        # Convert training image to RGB
        train_image_rgb = cv2.cvtColor(train_image, cv2.COLOR_BGR2RGB)

        try:
            train_encoding = face_recognition.face_encodings(train_image_rgb)[0]
            known_face_encodings = [train_encoding]
            known_face_names = ["Trained User"]  # Name for the training image
            print("Training image encoded successfully.")
        except IndexError:
            print(f"No face found in training image: {train_image_path}")
            exit()

        # Save the encodings and names to a file
        with open(DEFAULT_ENCODING_FILE_PATH, 'wb') as f:
            pickle.dump((known_face_encodings, known_face_names), f)
            print(f"Encodings saved to {DEFAULT_ENCODING_FILE_PATH}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python train_faces.py <train_image_path>")
        sys.exit(1)

    train_image_path = sys.argv[1]
    main(train_image_path)
