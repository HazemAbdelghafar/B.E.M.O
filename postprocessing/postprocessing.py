from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import find_dotenv, dotenv_values
import os
import random
import time

class PreProcessing:
    """
    A class to preprocess the result of a task into a natural, engaging response.
    """
    def __init__(self) -> None:
        """
        Initialize the PreProcessing class.
        
        Args:
            None
        
        Returns:
            None
        """
        random.seed(time.time())
        os.environ["GOOGLE_API_KEY"] = dotenv_values(find_dotenv())["GEMINI_API_KEY_TEST"] #! Test
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.9,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.prompt = self._init_prompt()
        self.chain = self._init_chain()
        self.error_responses = [
            "Hmm, something went wrong there. Want to try again?",
            "Oops! That didn't go as planned. Let's give it another shot.",
            "Uh-oh, looks like I ran into a hiccup. Can you check that for me?",
            "Sorry, I couldn't handle that request. Maybe try rephrasing it?",
            "Yikes, I hit a snag. Let's see if we can fix it together.",
            "Oh no, that didn't work. How about trying again?",
            "Hmm, I couldn't get that done. Maybe double-check the details?",
            "Looks like I need a little help with this one. Care to try again?",
            "Something didn't click on my end. Let's take another crack at it.",
            "Whoops! I missed the mark. Mind giving it another go?",
            "Sorry about that! I'm here if you want to try once more.",
            "That didn't work out. Let's reset and try again.",
            "Oops, I fumbled that one. Can you give me another chance?",
            "Hmm, I hit a roadblock. Let's try something different.",
            "Looks like something went sideways. Let's figure it out together.",
            "Sorry, I stumbled there. Want to have another go?",
            "Oh no, I couldn't complete that. Let me know how I can help.",
            "Oops, I got stuck. Want to check and try again?",
            "Hmm, that's on me. How about we try a different approach?",
            "Something didn't work out. Let's retry and get it right!"
        ]
        self.tasks = ["rapid questions", "smart home", "todo", "mail", "learning resources"]
        
    def _init_prompt(self) -> PromptTemplate:
        """
        Initialize the prompt for the task.
        
        Args:
            None
            
        Returns:
            PromptTemplate: The prompt for the task.
        """
        
        return PromptTemplate.from_template(
"""
Generate a fun and conversational response to be said by the TTS system.
Your task is to preprocess the result of a performed task into a natural, engaging response.
You are not performing the task; this is only for creating a response based on the given input.

Parameters:
- Result: {task_result}
    - The outcome of the task. This can be:
        - A boolean (`True` or `False`) indicating success or failure.
        - A number that should be mentioned naturally in the response.
        - A string representing the outcome, rephrased for clarity and conversational tone.
        - A dictionary with specific details about the result.
        - A list of items or results that should be mentioned in the response.

- User Query: {user_query}
    - The user's original request, providing context for the task.

- Task: {task_name}
    - One of the following types:
        - "rapid questions": The user asks BEMO a general knowledge or factual question.
        - "smart home": The user controls smart home appliances through BEMO.
        - "todo": The user adds or manages tasks in their Google Todo list.
        - "mail": The user sends, receives, or organizes emails using Gmail.
        - "learning resources": The user searches for educational resources about a specific topic.

Guidelines:
    - Ensure the response is conversational, concise, and engaging.
    - Do not repeat the input details explicitly; craft the response naturally.
    - Avoid using asterisks, emojis, or overly lengthy explanations.
    - Do not include any personal or sensitive information in the response.
    - No Emojies or special characters
    - If you think that the result is wrong, do not correct it. Just reflect the result in the response.
    - Do not attempt to correct blatantly wrong results or perform the task. Simply reflect the given result in the response.
    - Make sure the tone aligns with BEMO's friendly and interactive personality.
    - Focus on delivering a short and lighthearted message that reflects the result.

Your output should be a single, concise, and natural string for BEMO's TTS system.
"""
        )

            
    def _init_chain(self):
        """
        Initialize the chain for the task.
        
        Args:
            None
        
        Returns:
            Chain: The chain for the task.
        """
        return self.prompt | self.llm
    
    def __call__(self, task_result: str, user_query: str, task_name: str) -> str:
            """
            Process the user query and task result to generate a response.

            Args:
                task_result (str): The result of the task.
                user_query (str): The user's query.
                task_name (str): The name of the task.

            Returns:
                str: The generated response.
            """
            
            if task_name not in self.tasks:
                return self.error_responses[random.randint(0, len(self.error_responses)-1)]
            
            if user_query == "" or task_result == "" or task_name == "":
                return self.error_responses[random.randint(0, len(self.error_responses)-1)]
            
            try:
                response = self.chain.invoke(
                    input={
                        "task_result": task_result,
                        "user_query": user_query,
                        "task_name": task_name
                    }
                )
                try:
                    response = response.content.strip()
                except:
                    response = self.error_responses[random.randint(0, len(self.error_responses)-1)]
            except:
                response = self.error_responses[random.randint(0, len(self.error_responses)-1)]
                
            return response
        
        
    
    
if __name__ == "__main__":
    pp = PreProcessing()
    # task_result = {
    #     "result": "Paris",
    # }
    task_result = True
    # task_result = [
    #     {
    #         "id": "QU5ydjN6OEJ2NGZIMklINQ",
    #         "list_id": "MTE3NDYyMDEyNzE5NTgwODc4Njc6MDow",
    #         "name": "HI",
    #         "list_name": "My Tasks",
    #         "last_updated": "2024-11-20 00:18:07",
    #         "due_date": "2024-11-29 02:00:00",
    #         "completed_date": None,
    #         "is_done": False,
    #         "notes": None,
    #         "parent_id": None,
    #         "last_updated_relative": "1 hour ago, 26 minutes ago",
    #         "completed_date_relative": None,
    #         "due_date_relative": "23 hours from now, 44 minutes from now",
    #         "parent_title": None
    #     },
    #     {
    #         "id": "MkZPeDJlMWFhdUEtbFBLQw",
    #         "list_id": "MTE3NDYyMDEyNzE5NTgwODc4Njc6MDow",
    #         "name": "HI 2",
    #         "list_name": "My Tasks",
    #         "last_updated": "2024-11-20 00:13:17",
    #         "due_date": None,
    #         "completed_date": None,
    #         "is_done": False,
    #         "notes": None,
    #         "parent_id": "QU5ydjN6OEJ2NGZIMklINQ",
    #         "last_updated_relative": "1 hour ago, 31 minutes ago",
    #         "completed_date_relative": None,
    #         "due_date_relative": None,
    #         "parent_title": "HI"
    #     },
    #     {
    #         "id": "UG1IUjVJZFlwMWc5NFBjSg",
    #         "list_id": "MlJJN0F4WjVFVVJDWkhlUQ",
    #         "name": "Test 1 Updated",
    #         "list_name": "Test List",
    #         "last_updated": "2024-11-20 01:28:52",
    #         "due_date": "2024-11-30 02:00:00",
    #         "completed_date": None,
    #         "is_done": False,
    #         "notes": "Test 1 Updated Notes\n\nB.E.M.O",
    #         "parent_id": None,
    #         "last_updated_relative": "10 minutes ago, 33 seconds ago",
    #         "completed_date_relative": None,
    #         "due_date_relative": "23 hours from now, 44 minutes from now",
    #         "parent_title": None
    #     },
    #     {
    #         "id": "VU9seWg4b2tBTzF5M0kwUQ",
    #         "list_id": "MlJJN0F4WjVFVVJDWkhlUQ",
    #         "name": "Test 1 Updated",
    #         "list_name": "Test List",
    #         "last_updated": "2024-11-20 01:27:18",
    #         "due_date": "2024-11-30 02:00:00",
    #         "completed_date": None,
    #         "is_done": False,
    #         "notes": "Test 1 Updated Notes\n\nB.E.M.O",
    #         "parent_id": None,
    #         "last_updated_relative": "12 minutes ago, 7 seconds ago",
    #         "completed_date_relative": None,
    #         "due_date_relative": "23 hours from now, 44 minutes from now",
    #         "parent_title": None
    #     }
    # ]
    user_query = "Send an email to John Doe."
    task_name = "mail"
    response = pp(str(task_result), str(user_query), str(task_name))
    print(response)