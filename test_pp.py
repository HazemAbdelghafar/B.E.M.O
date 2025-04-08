import paho.mqtt.client as mqtt  # Import the MQTT client library for Python
import json  # Import json to handle message formatting


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

# Define broker address and topic
BROKER = "localhost"  # The MQTT broker address (localhost for local testing)
# TOPIC = "task_classifier/prompt"
SUB_TOPIC = "server/main"
TOPIC = "preprocessing/prompt"

# Create a new MQTT client instance
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "server")
# Connect the client to the broker

# Add a callback function to handle messages received from the broker
def on_message(client, userdata, message):
    """
    Callback function to handle messages received from the broker.
    
    Args:
        client: The MQTT client instance.
        userdata: User-defined data of any type.
        message: The message received from the broker.
    """
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")
    
# Set the callback function for when a message is received
client.on_message = on_message

client.connect(BROKER, 1883, 60)  # Default MQTT port is 1883, timeout is 60 seconds

# Subscribe to the topic
client.subscribe(SUB_TOPIC, qos=1)  # Subscribe to the topic with QoS level 1

send = {
        'predicted_labels': ['general'],
        'preprocessed_prompt': 'what is the weather like today',
        'module_name': 'task_classifier'
    }
send = {
        'predicted_labels': ['general'],
        'preprocessed_prompt': 'what about tomorrow',
        'module_name': 'task_classifier'
    }
send = {
        'predicted_labels': ['smart_home', 'todo', 'general'],
        'preprocessed_prompt': 'light up the living room then schedule a doctor appointment at 11 pm and whats the weather like today',
        'module_name': 'task_classifier'
    }
# send = {"prompt": "Hey Bemo, light up the living room and turn of the tv and the fan"}
# send = {
#         'predicted_labels': ['test'],
#         'preprocessed_prompt': 'My name is Ali and I am a software engineer. I am working on a project that involves using MQTT for communication.',
#         'module_name': 'task_classifier'
#     }
# send = {
#         'predicted_labels': ['test'],
#         'preprocessed_prompt': 'What is my job title and what is my name?',
#         'module_name': 'task_classifier'
#     }

client.loop_start()  # Start the MQTT client loop

# Publish the message to the defined topic
client.publish(TOPIC, json.dumps(send))  # Use json.dumps to serialize dict properly
print(f"Message published to topic {TOPIC}")

# Optional: Keep running briefly to allow message receipt
import time
time.sleep(10)

# client.disconnect()  # Disconnect the client
# print("Disconnected from the broker")
