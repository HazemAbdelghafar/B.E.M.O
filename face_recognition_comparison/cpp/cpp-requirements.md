Here's the updated **README** with the **Git clone commands** for downloading the required models:

---

# Face Recognition C++ Project

This project implements face recognition using Dlib and OpenCV. The system uses Haar cascades or HOG for face detection and Dlib's ResNet model for face recognition.

## **Setup Instructions**

### **1. Install Dependencies**

#### Linux (e.g., Ubuntu 18.04+):

```bash
sudo apt update
sudo apt install -y cmake g++ wget unzip libopencv-dev
```

#### macOS:

```bash
brew install opencv cmake
brew link opencv
brew install pkg-config
```

### **2. Clone the Repository**

```bash
git clone https://github.com/your-username/FaceRecognitionCpp.git
cd FaceRecognitionCpp
```

### **3. Pre-trained Models**

You need to download the following pre-trained models and place them in the `models/` directory:

#### Haar Cascade Model (Face Detection)

```bash
git clone https://github.com/opencv/opencv.git
cp opencv/data/haarcascades/haarcascade_frontalface_default.xml ./models/
```

#### Dlib Shape Predictor (Landmarks Detection)

```bash
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
mv shape_predictor_68_face_landmarks.dat ./models/
```

#### Dlib ResNet Face Recognition Model

```bash
wget http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2
bzip2 -d dlib_face_recognition_resnet_model_v1.dat.bz2
mv dlib_face_recognition_resnet_model_v1.dat ./models/
```

Your `models/` directory should look like this:

```plaintext
models/
├── haarcascade_frontalface_default.xml
├── shape_predictor_68_face_landmarks.dat
├── dlib_face_recognition_resnet_model_v1.dat
```

### **4. Build the Project**

#### Using CMake:

```bash
mkdir build
cd build
cmake ..
make
```

### **5. Run the Application**

#### Example Command:

```bash
./FaceRecognitionCpp <path_to_image>
```

For example:

```bash
./FaceRecognitionCpp ../images/test_image.jpg
```

---

## **Features**

-   **Face Detection**:
    -   Haar cascades or HOG.
-   **Face Recognition**:
    -   Uses Dlib’s ResNet-based model for feature extraction and comparison.

## **Requirements**

-   **C++ Compiler** (GCC/Clang)
-   **OpenCV 3.4.1 or higher**
-   **Dlib**
-   **CMake**

## **Directory Structure**

```plaintext
FaceRecognitionCpp/
├── build/                # Build directory
├── images/               # Sample images
├── models/               # Pre-trained models
├── include/              # Header files
├── src/                  # Source code
├── CMakeLists.txt        # CMake configuration
├── README.md             # Project documentation
```

---

Let me know if you need further modifications!
