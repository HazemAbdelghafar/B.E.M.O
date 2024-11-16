import face_recognition
import pickle
import sys

# Default output file path
DEFAULT_OUTPUT_FILE = "known_face_encodingmp.pkl"

def main(known_image_path):
    # Load and encode the known image
    print(f"Processing training image: {known_image_path}")
    known_image = face_recognition.load_image_file(known_image_path)

    known_face_encodings = face_recognition.face_encodings(known_image)

    if not known_face_encodings:
        print("No face found in the known image!")
        return

    # Save the encoding to the default file
    with open(DEFAULT_OUTPUT_FILE, "wb") as f:
        pickle.dump(known_face_encodings[0], f)

    print(f"Face encoding saved to {DEFAULT_OUTPUT_FILE}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python train_faces.py <known_image_path>")
        sys.exit(1)

    known_image_path = sys.argv[1]

    main(known_image_path)
