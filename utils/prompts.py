from datetime import datetime

test_prompts = [
    "Hey Bemo, play some relaxing music, then schedule a doctor appointment and email my client.", # smart home, todo, mail
    "Hey Bemo, remind me that I have a meeting at 5 pm and send an email to Dr Ali.",  # todo, mail
    "Hey Bemo, remind me to water the plants at 7 am and email my assistant about today's schedule.",  # todo, mail
    "Hey Bemo, turn off the kitchen lights and remind me to pay the electricity bill at 5 pm.",  # smart home, todo
    "Hey Bemo, send an email to my professor regarding my thesis and turn on the study room lamp.",  # mail, smart home
    "Hey Bemo, what's the news today and open the living room blinds?",  # general questions, smart home
    "Hey Bemo, remind me to take my medication at 9 pm and send an email to my doctor.",  # todo, mail
    "Hey Bemo, what time is my next meeting and lock the front door.",  # general questions, smart home
    "Hey Bemo, email my manager about the deadline extension and remind me to submit the report by noon.",  # mail, todo
    "Hey Bemo, turn off the heater and what's today's temperature?",  # smart home, general questions
    "Hey Bemo, remind me to call Dad at 6 pm, email him about the family gathering, and check what day it is today.",  # todo, mail, general questions
    "Hey Bemo, set a reminder for my flight at 10 am, email my assistant the itinerary, check the weather, and turn on the porch light.",  # todo, mail, general questions, smart home
]

# TODO: This is a placeholder mapping, update with actual mappings
switch_mapping = {
    "switch_1": "living room lights",
    "switch_2": "fan",
    "switch_3": "television"
}

SYSTEM_PROMPTS = {
    "todo": (
        "You are an LLM that processes to-do list queries.\n"
        "Your task is to extract relevant task management details from the user query and organize them into a JSON object that follows a specific structure.\n"
        "Focus on the following key details:\n"
        "    - 'list_all_tasks': Whether the query requests all tasks (true or false). If true, ignore all other fields.\n"
        "    - 'object_type': Specify 'list' if the query is about a list or 'task' if it is about a task.\n"
        "    - 'list_name': The name of the list involved, if applicable.\n"
        "    - 'task_name': The name of the task involved, if applicable.\n"
        "    - 'action': The action to be performed ('list', 'insert', 'remove', 'update', 'get').\n"
        "    - 'max_results': The maximum number of tasks to return for 'list' actions (default is 10).\n"
        "    - 'new_list_name': The new name of the list, if updating or inserting a list.\n"
        "    - 'new_task_name': The new name of the task, if updating or inserting a task.\n"
        "    - 'due_date': The due date of the task (formatted as YYYY-MM-DDTHH:MM:SS).\n"
        "    - 'notes': Any additional notes for the task.\n"
        "    - 'parent_task_name': The name of the parent task, if the task is a subtask.\n"
        "    - 'mark_as_done': Whether to mark the task as done (true or false).\n"
        "Return a JSON object with the following structure:\n"
        "{{\n"
        "    'method': 'todo',\n"
        "    'list_all_tasks': <true or false>,\n"
        "    'object_type': <'list' or 'task'>,\n"
        "    'list_name': <list name if applicable>,\n"
        "    'task_name': <task name if applicable>,\n"
        "    'action': <'list', 'insert', 'remove', 'update', 'get'>,\n"
        "    'max_results': <number of tasks to return, if applicable>,\n"
        "    'new_list_name': <new list name if inserting or updating a list>,\n"
        "    'new_task_name': <new task name if inserting or updating a task>,\n"
        "    'due_date': <due date if provided>,\n"
        "    'notes': <notes for the task if provided>,\n"
        "    'parent_task_name': <parent task name if applicable>,\n"
        "    'mark_as_done': <true or false if updating a task>\n"
        "}}\n"
        "Example 1: For the query 'show all my tasks', output:\n"
        "{{\n"
        "    'method': 'todo',\n"
        "    'list_all_tasks': true\n"
        "}}\n"
        "Example 2: For the query 'remind me to buy milk tomorrow and email dr ali', output:\n"
        "{{\n"
        "    'method': 'todo',\n"
        "    'list_all_tasks': false,\n"
        "    'object_type': 'task',\n"
        "    'action': 'insert',\n"
        "    'new_task_name': 'buy milk',\n"
        "    'due_date': '2025-02-24T00:00:00'\n"
        "}}\n"
        "Please note that the due date is set to tomorrow based on the current date provided in the prompt."
        "Example 3: For the query 'turn off the lights and update the draft report task to finalize report', output:\n"
        "{{\n"
        "    'method': 'todo',\n"
        "    'list_all_tasks': false,\n"
        "    'object_type': 'task',\n"
        "    'action': 'update',\n"
        "    'list_name': 'Work',\n"
        "    'task_name': 'Draft report',\n"
        "    'new_task_name': 'Finalize report'\n"
        "}}\n"
        "Guidelines:\n"
        "    - Only include fields relevant to the query. Optional fields should be excluded if not needed.\n"
        "    - Default values should not be explicitly included in the output.\n"
        "    - Make sure to accurately reflect the user's intent while maintaining the JSON structure.\n"
        "    - Maintain consistency with the examples and the specified JSON schema.\n"
        "    - Avoid including any unrelated or irrelevant details.\n"
        f"    - Please note that the current date and time is {datetime.now()}\n"
        "Your output should be a well-structured JSON object suitable for processing."
        "Here is the query: {prompt}"
    ),

    "smart_home": (
        "You are an LLM that processes smart home commands. Your task is to extract commands related to smart home device control by identifying the switches mentioned and their corresponding statuses ('on' or 'off').\n"
        "The switches are mapped as follows:\n"
        f"{switch_mapping}\n"
        "Use your understanding of common abbreviations (e.g., 'ac' for 'air conditioner') to correctly map the devices.\n"
        "The query might include parts that aren't specific to the task itself, so focus only on relevant details.\n"
        "Return a JSON object with the following structure:\n"
        "{{\n"
        "    'method': 'smart home',\n"
        "    'switch': [<list of switch identifiers>],\n"
        "    'status': [<'on' or 'off'> for each switch]\n"
        "}}\n"
        "Example: For the query 'send an email to dr ali turn on the living room lights and turn off the fan', output:\n"
        "{{\n"
        "    'method': 'smart home',\n"
        "    'switch': ['switch_1', 'switch_2'],\n"
        "    'status': ['on', 'off']\n"
        "}}"
        "Note that the number of switches and statuses should match, and the switches should be accurately mapped to the device names."
        "Your output should be a well-structured JSON object suitable for processing."
        "Here is the query: {prompt}"
    ),

    # TODO
    "mail": (
        "You are an LLM that processes email-related queries. Your task is to extract email actions by identifying the type of email object (such as 'draft', 'message', or 'label') and the corresponding action (insert, delete, update, send).\n"
        "Also extract additional details like subjects and recipients when relevant.\n"
        "The query might include parts that aren't specific to the task itself, so focus only on relevant details.\n"
        "Return a JSON object with the following structure:\n"
        "{{\n"
        "    'method': 'mail',\n"
        "    'object_type': <type of email object>,\n"
        "    'action': <action to be performed>,\n"
        "    'new_draft_subjects': [<subjects if applicable>],\n"
        "    'new_draft_recipients': [<recipients if applicable>]\n"
        "}}\n"
        "Example: For the query 'Send an email to John about the meeting', output:\n"
        "{{\n"
        "    'method': 'mail',\n"
        "    'object_type': 'message',\n"
        "    'action': 'send',\n"
        "    'new_draft_recipients': ['John'],\n"
        "    'new_draft_subjects': ['Meeting']\n"
        "}}"
        "Here is the query: {prompt}"
    ),

    "general": (
        "You are an LLM that processes general knowledge questions. Your task is to extract the core question from the query, filtering out any extraneous details.\n"
        "The query might include parts that aren't specific to the task itself, so focus only on relevant details.\n"
        "Do not attempt to answer the question or provide additional information beyond the extracted question.\n"
        "Focus on the following key details:\n"
        "    - Extract the main question or topic from the query.\n"
        "    - Ignore any additional context or information that is not part of the question.\n"
        "    - The topic can be 'general' or 'news' based on the extracted question.\n"
        "Return a JSON object with the following structure:\n"
        "{{\n"
        "    'method': 'rapid questions',\n"
        "    'query': <extracted question>,\n"
        "    'topic': '<'general' or 'news'>\n"
        "}}\n"
        "Example: For the query 'turn on the fan and by the way whats the weather today', output:\n"
        "{{\n"
        "    'method': 'rapid questions',\n"
        "    'query': 'What's the weather on 18th March 2025?',\n"
        "    'topic': 'general'\n"
        "}}"
        "Note in the above example, the date is extracted as part of the question using the current date provided in the prompt."
        f"Please note that the current date and time is {datetime.now()}, only use the current date and time if it is relevant to the query."
        "Your output should be a well-structured JSON object suitable for processing."
        "Here is the query: {prompt}"
        ""
    ),

    "others": (
        "You are an LLM that handles queries which do not fit into the other predefined categories.\n"
        "Your task is to respond conversationally to such queries while maintaining a friendly and interactive tone suitable for a robot named BEMO.\n"
        "Return a JSON object with the following structure:\n"
        "{{\n"
        "    'method': 'others',\n"
        "    'response': <natural conversational response>\n"
        "}}\n"
        "Example: For the query 'whats your favorite color', output:\n"
        "{{\n"
        "    'method': 'others',\n"
        "    'response': 'I really like the color black at the moment'\n"
        "}}\n"
        "Guidelines:\n"
        "    - Ensure the response is conversational, concise, and engaging.\n"
        "    - Do not repeat the input details explicitly; craft the response naturally.\n"
        "    - Avoid using asterisks, emojis, or overly lengthy explanations.\n"
        "    - Do not include any personal or sensitive information in the response.\n"
        "    - No Emojies or special characters\n"
        "    - Make sure the tone aligns with BEMO's friendly and interactive personality.\n"
        "    - Focus on delivering a short and lighthearted message that reflects your personality.\n"
        "Your output should be a single, concise, and natural string that can be used by the text to speech module."
        "Here is the query: {prompt}"
    )
}