cmake_minimum_required(VERSION 3.10)
project(FaceRecognition)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 14)

# Find OpenCV
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

# Find Dlib
find_package(dlib REQUIRED)
include_directories(${DLIB_INCLUDE_DIRS})

# Add the executables
add_executable(face_reco src/face_reco.cpp)
add_executable(take_photos src/take_photos.cpp)

# Link libraries
target_link_libraries(face_reco ${OpenCV_LIBS} dlib::dlib)
target_link_libraries(take_photos ${OpenCV_LIBS} dlib::dlib)
