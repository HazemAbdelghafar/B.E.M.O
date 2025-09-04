# **BEMO System Architecture**

## Overview

BEMO follows a **modular star architecture**. All components communicate **only** with a central hub called the `*_main_handler`. No direct communication occurs between individual modules; every request or response is routed through the `*_main_handler`.

## **Communication Design**

-   **Between Modules:**

    Internal communication between modules is handled using **MQTT**.

    -   Modules written in Python use dictionaries (`dict`) to send and receive messages.
    -   Modules written in C++ use maps (`map`).

-   **Between Server and Raspberry Pi:**

    External communication between the Raspberry Pi and the cloud server is done using **WebSockets**.

---

## **System Components**

BEMO’s functionality is divided into two main component types:

### **1. Modules**

-   Long-running programs (daemons) that stay active and wait for MQTT messages.
-   Each module listens on a specific MQTT topic and performs its job when triggered.
-   Examples include:
    -   `SR` (Speech Recognition)
    -   `TTS` (Text-to-Speech)
    -   `wake_word_detector` (Wake Word Detection)
    -   `DOA` (Direction of Arrival)
    -   `pre-processing` (Pre-Processing)

### **2. Scripts**

-   Lightweight, short-lived programs.
-   Executed on demand, then terminated immediately after completing their task.
-   Example:
    -   The authentication script that captures a photo and performs face recognition.

---

## **Error Handling**

The system has error handling implemented throughout all modules. If any error occurs, the system prevents freezing or crashing by either returning a generic error message to the user or attempting to recover automatically when possible.

---

## **BEMO – Raspberry Pi Pipeline**

**Hardware Specs:**

-   **Model:** Raspberry Pi 5
-   **RAM:** 8 GB
-   **OS:** 64-bit Raspberry Pi OS Bookworm
-   **Storage:** 32 GB microSD card
-   **CPU:** 4x Cortex-A76 cores

---

### **1. Wake Word Detection**

-   The user says the wake word: **"Bumble"**.
-   The audio is captured by the **ReSpeaker Mic Array v2.0**.

---

### **2. Wake Word Acknowledgement**

-   The `wake_word_detector` module detects the wake word and publishes a message to the `rpi_main_handler`.

---

### **3. Wake Word Response and Initialization**

Upon receiving the wake word detection signal, `rpi_main_handler` triggers the following actions:

#### **3.1 TTS Acknowledgement**

-   The `TTS` module is instructed to respond with a predefined phrase (e.g., _"Uh-uh"_, _"Yes"_, _"I am here"_ ) using one of two options:
    -   **Offline:** `tacotron2-DDC_ph`
    -   **Online:** `Edge TTS`
-   The output is played through the **Excefore 3-Watt 4-Ohm Speaker**.
-   Once playback is complete, the `TTS` module notifies `rpi_main_handler` that it is done — ensuring the robot does not record its own response.

#### **3.2 Screen Animation**

-   The `screen` module is instructed to animate the **Wisecoco ST7701S 2.8-inch screen**, showing the robot **opening its eyes**.

#### **3.3 Direction of Arrival (DOA)**

-   The `DOA` module calculates the user's direction using the **4 microphones** on the **ReSpeaker Mic Array v2.0**.
-   The direction is quantized into **8 segments** across 360 degrees.
-   The module averages the **last 5 values** and publishes the resulting direction to `rpi_main_handler`.

---

### **4. Body Rotation**

-   Once the average direction is received, `rpi_main_handler` sends it over **UART** to the **MiiElAOD RPI 5 Robot Expansion Board**.
-   The board controls the **4 N20 motors** to rotate the robot to face the user.

---

### **5. Listening for User Speech**

Upon completion of the initial TTS response:

#### **5.1 Recording and Speech Recognition**

-   The `record` script is executed, which records until **1.5 seconds of silence** are detected.
-   Once recording ends, the `SR` (Speech Recognition) module starts, using **Whisper C++** to transcribe the audio.
-   The transcription is published back to the `rpi_main_handler`.

#### **5.2 Eye Movement Animation**

-   The `screen` module animates the **Wisecoco screen** to show the robot **moving its eyes**, indicating active listening.

---

### **6. Emotion Recognition**

-   After receiving the recognized speech, `rpi_main_handler` forwards it to the `emotion_recognition` module.
-   The module uses **`roberta-base-go_emotions`** to infer the **top 3 emotions** and their **respective probabilities**.
-   The results are sent back to `rpi_main_handler`.

---

### **7. User Feedback and Server Communication**

Upon receiving emotion results, `rpi_main_handler` performs the following:

#### **7.1 TTS Response**

-   A confirmation message (e.g., _"I’m on it"_, _"Starting now"_ ) is sent to the `TTS` module.
-   Speech synthesis is handled via:
    -   **Offline:** `tacotron2-DDC_ph`
    -   **Online:** `Edge TTS`
-   Output is played through the **Excefore speaker**.

#### **7.2 Forwarding to Server**

-   The `ws_robot` module receives:
    -   Recognized text
    -   Inferred emotions
    -   `robot_id`
-   It transmits the data over **WebSockets** as **JSON** to the forwarding web service.

---

### **8. Server Response Handling**

Once `rpi_main_handler` receives a result from the `ws_robot` module, it falls into one of two categories:

---

#### **8.1 Authentication Request**

##### **8.1.1 Prompting the User**

-   `TTS` module is triggered to prompt the user to **face the camera** using predefined instructions (offline or online TTS).
-   Playback is done through the **Excefore speaker**.

##### **8.1.2 Capturing the Image**

-   After TTS is complete, the `camera_capture` script is executed.
-   It captures an image and saves it to a predefined directory.

##### **8.1.3 Face Recognition**

-   The `face_recognition` script is then launched.
-   It compares the captured image to the stored user image and returns one of the following results:
    -   `user_authenticated`
    -   `user_not_authenticated`
    -   `no_face_found`

##### **8.1.4 Sending Result**

-   Once a result is received, `rpi_main_handler` sends it back to `ws_robot`, which forwards it over WebSockets to the web service.

---

#### **8.2 Final Response**

##### **8.2.1 Responding to the User**

-   The `TTS` module is instructed to vocalize the **server-generated response**, using either offline or online TTS.
-   Playback occurs through the **Excefore speaker**.

##### **8.2.2 Displaying the Emotion**

-   The `screen` module is instructed to reflect the **robot’s emotion** on the **Wisecoco screen**.

---

## **Render Web Service (Forwarding Web Service)**

**Deployment Specs:**

-   **CPU:** 0.1 Core
-   **Memory:** 512 MB RAM
-   **Storage:** No persistent memory (stateless)

---

### **1. Message Reception and Routing**

-   The Forwarding Web Service receives a WebSocket message.
-   It parses the incoming message into a **Python dictionary** and determines the **source** of the message — whether it came from a **robot** or from the **server**.

---

#### **1.1 If the Message Originated from a Robot**

-   The service checks whether the **server is currently reachable and online**:

    ##### **1.1.1 Server is Online**

    -   The message is **forwarded to the server**.

    ##### **1.1.2 Server is Offline**

    -   The service sends a response **back to the robot**, indicating that the **server is down**.

---

#### **1.2 If the Message Originated from the Server**

-   The service extracts the **target `robot_id`** from the message.
-   It checks if the **robot with the specified ID is currently connected**:

    ##### **1.2.1 Robot is Connected**

    -   The message is **forwarded to the target robot**.

    ##### **1.2.2 Robot is Not Connected**

    -   The service **takes no action**.

---

## **Server Specifications**

-   **OS:** Ubuntu 24.04 LTS
-   **CPU:** 11th Gen Intel i7-11800H @ 2.30GHz (8 cores, 16 threads)
-   **RAM:** 48 GB
-   **GPU:** NVIDIA GeForce RTX 3050
-   **Storage:** 512 GB SSD
-   **Network:** Killer E2600 Intel Ethernet Controller
-   **Environment:** Python 3.10.17, Mosquitto MQTT Broker v2.0.18

---

## **Processing Pipeline**

### **1. Incoming Message Handling**

-   The `ws_server` module receives an incoming WebSocket message.
-   The message is parsed into a **Python dictionary**.
-   A **new thread** is created to handle the request.
-   The request is then **published to the `server_main_handler`**.

---

### **2. Authentication Check**

Upon receiving the dictionary, the `server_main_handler` checks whether the message is a response to an **authentication request**:

#### **2.1 If Not an Authentication Response:**

-   The request enters the **standard pipeline**.
-   The prompt is published to the `task_classifier` module.
-   This module uses the `PromptToTask_MultiLabelClassifier_Optimized` model, trained on-site to detect tasks, to classify the prompt into one or more of the following categories:

    -   `general_questions`
    -   `smart_home`
    -   `todo`
    -   `mail`
    -   `finding_learning_resources`

#### **2.2 If an Authentication Response:**

-   The system evaluates the authentication outcome:

    -   **2.2.1** If the **user is authenticated**, the pipeline resumes from **Step 3.1**.
    -   **2.2.2** If **no face is detected**, it retries **Step 3.2** a predefined number of times. If still unsuccessful, the task is ignored.
    -   **2.2.3** If the **face is not authenticated**, it also retries **Step 3.2** a predefined number of times. If authentication fails again, the **robot is blocked**.

---

### **3. Task Authorization**

Upon receiving the classified task from the `task_classifier` module:

#### **3.1 If Task Does Not Require Authentication:**

-   The `server_main_handler` publishes the **task**, **emotions**, and **original prompt** to the `pre-processing` module.
-   This module uses **GEMINI-1.5-Flash** via **LangChain** to generate a Python dictionary that represents the user's intent in a task-specific format.

#### **3.2 If Task Requires Authentication:**

-   The system responds to the robot indicating that **authentication is required** and halts the pipeline.

---

### **4. Task Execution**

-   Once the `server_main_handler` receives the structured task dictionary from the `pre-processing` module, it forwards it to the `task_handler` module.
-   The `task_handler` determines the appropriate module to handle the task:

    -   `general_questions`, `smart_home`, `todo`, `mail`, or `finding_learning_resources`

-   The selected module processes the request and returns a result, which is sent back to the `server_main_handler`.

---

### **5. Response Generation**

-   The `server_main_handler` forwards the **task result**, **original prompt**, and **user emotions** to the `post-processing` module.
-   This module generates a **TTS-friendly response** and selects the **robot’s emotional state** using **GEMINI-1.5-Flash** and **LangChain**.

---

### **6. Final Response and Logging**

Upon receiving the final response and robot emotion from the `post-processing` module:

#### **6.1 WebSocket Delivery**

-   The response and emotion are published to the `ws_server` module with the corresponding `robot_id`.
-   The `ws_server` then sends this data to the **Forwarding Web Service** via WebSockets in **JSON** format.

#### **6.2 Data Logging**

-   The entire set of data collected through the pipeline is published to the `DB` module (pending implementation) for storage in a **remote database**.

---

### **System Notes**

-   **Blocking System:**
    A blocking mechanism is in place to prevent misuse. If a user attempts to access a task requiring authentication and fails, the system can **block the robot** for a specified duration. This is enforced at the **server level**.

-   **Chat History:**
    A chat history system tracks the most recent **3 to 10 conversations** per task. This is used to **contextualize future prompts**, enhancing continuity and understanding in user interactions.
