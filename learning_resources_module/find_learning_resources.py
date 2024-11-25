from langchain_community.tools import TavilySearchResults
from tavily import TavilyClient

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import chain, RunnableConfig

from dotenv import find_dotenv, dotenv_values

import os
import time
import requests
import json

DEFAULT_PATH = os.path.dirname(__file__)


class FindLearningResources:
    def __init__(
        self,
        use_llm: bool = True,
        max_results_per_type: int = 5,
        check_status_code: bool = False,
        clean_resources: bool = True,
    ):
        """
        Initialize the Tavily API and Google Chat API

        Args:
            use_llm (bool): Whether to use the LLM to generate responses. Default is True.
            max_results_per_type (int): The maximum number of results to return for each resource type. Default is 5.
            check_status_code (bool): Whether to check the status code of the resources. Default is False.
            clean_resources (bool): Whether to clean the resources. Default is True.

        Returns:
            None
        """

        # Set the parameters for the class
        self.use_llm = use_llm
        self.max_results_per_type = max_results_per_type
        self.check_status_code = check_status_code
        self.clean_resources = clean_resources

        # Load API keys from .env file
        self.tavily_api_key = dotenv_values(find_dotenv())[
            "TAVILY_API_KEY_TEST"
        ]  #! Remove _TEST

        if self.use_llm:
            self.gemini_api_key = dotenv_values(find_dotenv())[
                "GEMINI_API_KEY_TEST"
            ]  #! Remove _TEST

        # Set the API keys as environment variables
        if self.use_llm:
            os.environ["TAVILY_API_KEY"] = self.tavily_api_key
            os.environ["GOOGLE_API_KEY"] = self.gemini_api_key

        # Initialize the Tavily and Google Chat API
        if self.use_llm:
            self.tavily = TavilySearchResults(
                max_results=20,
                search_depth="advanced",
                include_answer=False,
                verbose=False,
                include_raw_content=False,
                include_images=True,
                exclude_domains=[],  # Todo: Add domains to exclude
            )
        else:
            self.tavily = TavilyClient(api_key=self.tavily_api_key)

        if self.use_llm:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
            )

        # Initialize the output
        if self.use_llm:
            self.output_parser = JsonOutputParser()

        # Initialize the prompt or resources
        if self.use_llm:
            self.prompt = self._init_prompt()
        else:
            self.resources = [
                "Learning Roadmaps",
                "Learning Blogs",
                "Learning Articles",
                "Learning YouTube Videos",
                "Scientific Papers",
                "Learning Courses",
                "Learning Figures",
                "Learning Diagrams",
                "Learning Charts",
                "Learning Infographics",
                "Learning Images",
                "Communities",
                "Forums",
                "Code Repositories",
                "Learning Slides",
                "Learning Presentations",
                "Learning Books",
                "Learning eBooks",
                "Learning Webinars",
                "Case Studies",
                "Real-world Applications",
                "Examples",
            ]

        # Initialize the chain
        if self.use_llm:
            self.chain = self._init_chain()

    def _init_prompt(self) -> ChatPromptTemplate:
        """
        Initialize the prompt with the given text

        Args:
            None

        Returns:
            ChatPromptTemplate: The initialized prompt
        """

        return ChatPromptTemplate(
            [
                (
                    "system",
                    """
                    You are an intelligent assistant specialized in finding high-quality learning resources on the web.
                    Your task is to gather diverse and comprehensive resources for the topic provided in the human input. Include the following resource types:
                    
                    - **Roadmaps**: Step-by-step guides or structured learning paths.
                    - **Blogs/Articles**: Informative written content explaining concepts, ideas, or updates related to the topic.
                    - **YouTube Videos**: Video tutorials, lectures, or explainers.
                    - **Scientific Papers**: Research papers or articles published in journals or conferences.
                    - **Courses**: Online courses, tutorials, or workshops (free or paid).
                    - **Images**: Visual resources such as diagrams, charts, or infographics related to the topic.
                    - **Podcasts**: Audio discussions or interviews related to the topic.
                    - **Communities/Forums**: Online platforms where the topic is actively discussed.
                    - **Code Repositories**: Open-source repositories with implementations or datasets.
                    - **Slides/Presentations**: Educational slide decks or conference presentations.
                    - **Books**: Textbooks, guides, or eBooks on the topic.
                    - **Datasets**: Public datasets relevant to the topic.
                    - **Interactive Tutorials**: Platforms offering hands-on learning experiences.
                    - **Webinars**: Live or recorded online events.
                    - **Case Studies**: Real-world applications and examples.
                    - **Newsletters**: Regular updates and insights about the topic.
                    
                    Rules:
                    - Include resources from as many different types as possible. Avoid focusing on only a few types.
                    - The total number of results must not exceed 20 and must not be less than 12.
                    - The more the number of results, the better, as long as quality is maintained.
                    - The total number of results for each resource type must not exceed 3.
                    - Select only the most relevant and high-quality resources for each type.
                    - Ensure a diverse selection to cater to different learning preferences and levels.
                    - Do not return duplicate resources or similar content.
                    - THE TOTAL NUMBER OF RESOURCES MUST BE BETWEEN 12 AND 20.

                    Provide the results in the following JSON format:
                    {{
                        "resources": [
                            {{"title": "Title of resource 1", "url": "URL of the resource 1", "type": "Type of the resource 1"}},
                            {{"title": "Title of resource 2", "url": "URL of the resource 2", "type": "Type of the resource 2"}},
                            {{"title": "Title of resource 3", "url": "URL of the resource 3", "type": "Type of the resource 3"}},
                            ...
                        ],
                        "model_output": "A short sentence describing all of the results for the user and telling them that the results have been sent to their phone on Telegram and to their machine on the B.E.M.O app."
                    }}
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

    def find_resources(self, topic: str) -> dict:
        """
        Find learning resources for the given topic

        Args:
            topic (str): The topic for which to find learning resources

        Returns:
            dict: The learning resources found for the given topic
        """

        if self.use_llm:

            # Define the tool chain
            @chain
            def tool_chain(user_input: str, config: RunnableConfig):
                input_ = {"user_input": user_input}
                try:
                    ai_msg = self.chain.invoke(input_, config=config)
                    tool_msgs = self.tavily.batch(ai_msg.tool_calls, config=config)
                    response = self.chain.invoke(
                        {**input_, "messages": [ai_msg, *tool_msgs]}, config=config
                    )
                except Exception as e:
                    response = {"error": str(e)}

                try:
                    parsed_output = self.output_parser.parse(response.content)
                except Exception as e:
                    parsed_output = {"error": str(e)}

                return parsed_output

            # Run the tool chain
            start_time = time.time()
            result = tool_chain.invoke(topic)

            # Add the time taken and topic to the result
            result["time_taken"] = round(time.time() - start_time, 2)
            result["topic"] = topic
            result["total_resources"] = len(result["resources"])

            if self.clean_resources:
                return self.clean_llm_resources(result)
            else:
                result["cleaning_time"] = 0
                return result

        else:
            # Todo: Implement the logic to find resources without the LLM
            pass

    def find_multiple_resources(self, topics: list) -> dict:
        """
        Find learning resources for the given topics

        Args:
            topics (list): The topics for which to find learning resources

        Returns:
            dict: The learning resources found for the given topics
        """

        results = []
        for topic in topics:
            results.append(self.find_resources(topic))
            print(f"Learning resources found for the topic '{topic}'")

        return results

    def clean_llm_resources(self, resources: dict) -> dict:
        """
        Clean the learning resources generated by the LLM

        Args:
            resources (dict): The learning resources generated by the LLM

        Returns:
            dict: The cleaned learning resources
        """

        start_time = time.time()

        allowed_status_codes = [
            200,
            201,
            202,
            203,
            204,
            205,
            206,
            207,
            208,
            226,
            300,
            301,
            302,
            303,
            304,
            305,
            306,
            307,
            308,
        ]

        # Remove duplicates based on the URL
        unique_resources = []
        unique_urls = set()
        for resource in resources["resources"]:
            url = resource["url"]
            if url not in unique_urls:
                unique_urls.add(url)
                unique_resources.append(resource)

        # Remove resources with empty titles or URLs
        unique_resources = [
            resource
            for resource in unique_resources
            if resource["title"] != ""
            and resource["url"] != ""
            and resource["type"] != ""
            and resource["url"] is not None
        ]

        # Limit the number of resources for each type to the maximum allowed
        resource_count = {}
        cleaned_resources = []
        for resource in unique_resources:
            resource_type = resource["type"]
            if resource_type not in resource_count:
                resource_count[resource_type] = 0
            if resource_count[resource_type] < self.max_results_per_type:
                cleaned_resources.append(resource)
                resource_count[resource_type] += 1

        # Limit the number of resources to 20
        if len(cleaned_resources) > 20:
            cleaned_resources = cleaned_resources[:20]

        # Remove the resources that give a status code other than 200
        if self.check_status_code:
            non_error_resources = []
            for resource in cleaned_resources:
                url = resource["url"]
                response = requests.request("GET", url)
                status_code = response.status_code
                if status_code in allowed_status_codes:
                    non_error_resources.append(resource)
        else:
            non_error_resources = cleaned_resources

        return {
            "resources": non_error_resources,
            "topic": resources["topic"],
            "total_resources": resources["total_resources"],
            "model_output": resources["model_output"],
            "generation_time": resources["time_taken"],
            "cleaning_time": round(time.time() - start_time, 2),
        }


if __name__ == "__main__":
    flr_llm = FindLearningResources(use_llm=True)

    topics = [
        "Deep Learning",
        "Arabic Language",
        "Stock Market Analysis",
        "Human Brain",
    ]

    results = flr_llm.find_multiple_resources(topics)

    with open(DEFAULT_PATH + "/test/resources.json", "w") as f:
        json.dump(results, f, indent=4)

    print(
        f"Learning resources for the topics '{topics}' using LLM saved to {DEFAULT_PATH}/test/resources.json"
    )

    for result in results:
        print(
            f"Topic: {result['topic']}, Number of Resources: {len(result['resources'])}"
        )
