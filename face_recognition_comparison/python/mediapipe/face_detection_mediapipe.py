import cv2
import mediapipe as mp
import face_recognition
import pickle
import sys
import json

# MediaPipe initialization
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

DEFAULT_ENCODED_FILE = "known_face_encodingmp.pkl"

def write_json(result, output_file="output.json"):
    """Write recognition result to a JSON file."""
    data = {"recognized": result}
    with open(output_file, "w") as f:
        json.dump(data, f)
    print(f"Result written to {output_file}: {data}")

def main(test_image_path):
    print(f"Loading encoded face from {DEFAULT_ENCODED_FILE}")
    try:
        with open(DEFAULT_ENCODED_FILE, "rb") as f:
            known_face_encoding = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: Encoded file {DEFAULT_ENCODED_FILE} not found!")
        write_json(0)
        return

    test_image = cv2.imread(test_image_path)
    if test_image is None:
        print("Error loading the test image!")
        write_json(0)
        return

    rgb_test_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)

    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(rgb_test_image)

        if results.detections:
            print(f"{len(results.detections)} face(s) detected.")

            # Recognize faces using face_recognition
            face_locations = face_recognition.face_locations(rgb_test_image)
            face_encodings = face_recognition.face_encodings(rgb_test_image, face_locations)

            recognized = 0  # Default: No match
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces([known_face_encoding], face_encoding)
                face_distances = face_recognition.face_distance([known_face_encoding], face_encoding)

                for match, dist in zip(matches, face_distances):
                    print(f"Match: {match}, Distance: {dist}")

                if True in matches:
                    print("Known Face Detected")
                    recognized = 1  # Match found
                    cv2.rectangle(test_image, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(test_image, "Known Face", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    break  # Stop checking once a match is found
            else:
                print("Unknown Face Detected")
                cv2.rectangle(test_image, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(test_image, "Unknown Face", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            # Write the recognition result to JSON
            write_json(recognized)
        else:
            print("No faces detected in the test image.")
            write_json(0)

    # Uncomment to display the result
    # cv2.imshow('Face Detection and Recognition', test_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python recognize_faces.py <test_image_path>")
        sys.exit(1)

    test_image_path = sys.argv[1]
    main(test_image_path)
