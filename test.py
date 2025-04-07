import paho.mqtt.client as mqtt  # Import the MQTT client library for Python


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
TOPIC = "preprocessing/prompt"

# Create a new MQTT client instance
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "python_publisher")
# Connect the client to the broker
client.connect(BROKER, 1883, 60)  # Default MQTT port is 1883, timeout is 60 seconds

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
# send = {
#         'predicted_labels': ['smart_home', 'todo', 'general'],
#         'preprocessed_prompt': 'light up the living room then schedule a doctor appointment at 11 pm and whats the weather like today',
#         'module_name': 'task_classifier'
#     }
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

client.publish(TOPIC, str(send))  # Publish the message to the defined topic
print(f"Message published to topic {TOPIC}")

client.disconnect()  # Disconnect the client
print("Disconnected from the broker")
