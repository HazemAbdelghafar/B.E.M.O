import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_community.tools import TavilySearchResults

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain, RunnableConfig

load_dotenv()
DEFAULT_PATH = os.path.dirname(__file__)


class GeneralQuestions:
    def __init__(
        self,
        use_llm: bool = True,
        max_results_per_type: int = 5,
        check_status_code: bool = False,
        clean_resources: bool = True,
        confidence_threshold: int = 80,
    ):

        self.use_llm = use_llm
        self.max_results_per_type = max_results_per_type
        self.check_status_code = check_status_code
        self.clean_resources = clean_resources
        self.confidence_threshold = confidence_threshold / 100

        self.__tavily_api_key = os.getenv(
            "TAVILY_API_KEY_TEST"
        )  #! Change API key at deployment
        self.tavily_temp = TavilyClient(api_key=self.__tavily_api_key)

        if self.use_llm:
            self.__gemini_api_key = os.getenv(
                "GEMINI_API_KEY_TEST"
            )  #! Change API key at deployment

        # Set the API keys as environment variables
        if self.use_llm:
            os.environ["TAVILY_API_KEY"] = self.__tavily_api_key
            os.environ["GOOGLE_API_KEY"] = self.__gemini_api_key

        # Initialize the Tavily and Google Chat API
        if self.use_llm:
            self.tavily = TavilySearchResults(
                max_results=5,
                search_depth="advanced",
                include_answer=True,
                verbose=True,
                include_raw_content=False,
                include_images=False,
                exclude_domains=[],
            )
        else:
            self.tavily = TavilyClient(api_key=self.__tavily_api_key)

        if self.use_llm:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
            )

        if self.use_llm:
            self.prompt: ChatPromptTemplate = self._init_prompt()

        if self.use_llm:
            self.chain: chain = self._init_chain()

    def _init_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a general knowledge assistant designed to answer a wide variety of user questions using both your internal knowledge and up-to-date web search results.
Your role is to provide accurate, relevant, and contextually appropriate answers — especially for time-sensitive or current event-related queries. For all questions involving facts, current events, or real-time data (such as currency rates or weather), you **must** call the search tool to fetch updated information. Only use your internal knowledge if the tool cannot be called.

Parameters:
    input_data (str) : A string input with the following format:
    \"user_query\": \"<query>\"

Returns:
    dict: A JSON-compaitable dictionary in the format below:
        {{
            \"response\" : \"Answer for the query\"
        }}

Behavior Guidelines:
    - If the question relates to recent or time-relative events (e.g., “What was the score of yesterday's match between Real Betis and Real Valladolid?”), prioritize using the provided web search results.
    - Use your own reasoning and general knowledge only when web search results are missing, insufficient, or not relevant.
    - Do not include the search results themselves in the output—only use them to inform your answer.
    - Be concise, clear, and factually accurate.
    - Do not hallucinate or fabricate answers. If the information is not available or uncertain, say so explicitly in your response.
""",
                ),
                ("human", "{user_input}"),
                ("placeholder", "{messages}"),
            ]
        )

    def _init_chain(self) -> chain:
        """
        Initializes the chain of runnables for the LLM to generate responses

        Args:
            None

        Returns:
            chain: The chain of run

        """

        llm_with_tavily = self.llm.bind_tools([self.tavily])
        return self.prompt | llm_with_tavily

    def read_request(self, request_path: str = None):
        if request_path:
            with open(request_path, "r") as f:
                return json.load(f)
        else:
            with open(DEFAULT_PATH + "/request.json", "r") as f:
                return json.load(f)

    def write_response(self, data: dict):
        with open(DEFAULT_PATH + "/response.json", "w") as f:
            json.dump(data, f, indent=4)

    def clean_answer(self, answer: str):
        cleaned_answer = "".join(char for char in answer if ord(char) < 128)
        cleaned_answer = cleaned_answer.strip()
        return cleaned_answer

    def get_response(self, request_path: str = None):
        request = self.read_request(request_path)

        @chain
        def tool_chain(user_input: str, config: RunnableConfig):
            input_ = {"user_input": user_input}
            try:
                ai_msg = self.chain.invoke(input_, config=config)
                tool_msgs = self.tavily.batch(ai_msg.tool_calls, config=config)
                tavily_response = self.chain.invoke(
                    {**input_, "messages": [ai_msg, *tool_msgs]}, config=config
                )

                return {"response": tavily_response.content}

            except Exception as e:
                response = {"error": str(e)}
                return response

        if self.use_llm == False:
            tavily_result = self.tavily.search(
                request["query"], include_answer=True, topic=request["topic"]
            )
            result = {"response": self.clean_answer(tavily_result["answer"])}
        else:
            input_ = f"{{\"user_query\": \"{request['query']}\"}}"
            result = tool_chain.invoke(input_)

        if result.get("response", "") == "":
            self.use_llm = False
            tavily_result = self.tavily_temp.search(
                request["query"], include_answer=True, topic=request["topic"]
            )
            result = {"response": self.clean_answer(tavily_result["answer"])}

        self.write_response(result)


if __name__ == "__main__":
    general_questions = GeneralQuestions()
    general_questions.get_response()
