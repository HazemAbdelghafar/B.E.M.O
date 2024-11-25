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
        clean_resources: bool = False,
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
            self.llm_resources = [
                "Roadmaps",
                "Blogs/Articles",
                "YouTube Videos",
                "Scientific Papers",
                "Courses",
                "Images",
                "Communities/Forums",
                "Code Repositories",
                "Slides/Presentations",
                "Books",
                "Webinars",
                "Case Studies",
            ]
        else:
            self.tavily_resources = [
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
Gather high-quality learning resources based on the specified topic and specific resource types.

Parameters:
    input_data (str): A string input with the following format:
    "Topic: <topic> - Specific Resources: <resource1>, <resource2>, ..."

Resource Types:
    - Roadmaps: Step-by-step guides or structured learning paths.
    - Blogs/Articles: Informative written content explaining concepts or updates.
    - YouTube Videos: Video tutorials, lectures, or explainers.
    - Scientific Papers: Research papers or articles published in journals or conferences.
    - Courses: Online courses, tutorials, or workshops (free or paid).
    - Images: Visual resources like diagrams, charts, or infographics.
    - Communities/Forums: Online platforms discussing the topic.
    - Code Repositories: Open-source repositories with implementations or datasets.
    - Slides/Presentations: Educational slide decks or conference presentations.
    - Books: Textbooks, guides, or eBooks on the topic.
    - Webinars: Live or recorded online events.
    - Case Studies: Real-world applications and examples.

Rules:
    - Include resources from multiple types, not just a few.
    - Provide 12-20 results, prioritizing quality and variety.
    - The output should be in JSON format.
    - Do not include the number of results in the "model_output".

Returns:
    dict: A JSON-compatible dictionary in the following format:
    {{
        "resources": [
            {{"title": "Title of resource 1", "url": "URL of the resource 1", "type": "Type of the resource 1"}},
            {{"title": "Title of resource 2", "url": "URL of the resource 2", "type": "Type of the resource 2"}},
            ...
        ],
        "model_output": "Summary of results sent to Telegram and B.E.M.O app."
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

    def find_resources(self, topic: str, specific_resources: list = None) -> dict:
        """
        Find learning resources for the given topic

        Args:
            topic (str): The topic for which to find learning resources
            specific_resources (list): The specific types of resources to include. Default is None which includes all resources.

        Returns:
            dict: The learning resources found for the given topic
        """

        if self.use_llm:

            # Check if specific resources are provided
            llm_resources = [resource.lower() for resource in self.llm_resources]
            specific_resources = [
                resource.lower()
                for resource in specific_resources
                if resource.lower() in llm_resources
            ]

            # Remove duplicates
            specific_resources = list(set(specific_resources))

            # Generate the input for the LLM
            if len(specific_resources) == 0 or specific_resources is None:
                specific_resources = llm_resources

            input = (
                f"Topic: {topic} - Specific Resources: {', '.join(specific_resources)}"
            )

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
            result = tool_chain.invoke(input)

            try:
                total_resources = len(result["resources"])
            except:
                return {"error": "LLM failed to generate resources."}

            # Add the time taken and topic to the result
            result["time_taken"] = round(time.time() - start_time, 2)
            result["topic"] = topic
            result["total_resources"] = total_resources
            result["specific_resources"] = specific_resources
            if self.clean_resources:
                return self.clean_llm_resources(result)
            else:
                result["cleaning_time"] = 0
                return result

        else:
            # Todo: Implement the logic to find resources without the LLM
            pass

    def find_multiple_resources(
        self, topics: list, specific_resources: list = [[]]
    ) -> list:
        """
        Find learning resources for the given topics

        Args:
            topics (list): The topics for which to find learning resources
            specific_resources (list): The specific types of resources to include for each topic. Default is [[]].

        Returns:
            dict: The learning resources found for the given topics
        """

        if len(specific_resources) != len(topics):
            return {
                "error": "The number of specific resources must match the number of topics."
            }

        results = []
        for topic, specific_resource in zip(topics, specific_resources):
            results.append(self.find_resources(topic, specific_resource))
            print(
                f"Learning resources found for the topic '{topic}', specific resources: {specific_resource}"
            )  #! Remove

        return results

    # Todo: Fix the function to clean the resources
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

        print(f"Unique resources: {len(unique_resources)}")  #! Remove

        # Remove resources with empty titles or URLs
        unique_resources = [
            resource
            for resource in unique_resources
            if resource["title"] != ""
            and resource["url"] != ""
            and resource["type"] != ""
            and resource["url"] is not None
        ]

        print(f"Resources with titles and URLs: {len(unique_resources)}")  #! Remove

        # Remove resource types that are not in the specific resources
        specific_resources = resources["specific_resources"]
        unique_resources = [
            resource
            for resource in unique_resources
            if resource["type"].lower() in specific_resources
        ]

        print(f"Resources with specific types: {len(unique_resources)}")  #! Remove

        # Limit the number of resources for each type to the maximum allowed
        if len(specific_resources) > 2:
            resource_count = {}
            cleaned_resources = []
            for resource in unique_resources:
                resource_type = resource["type"]
                if resource_type not in resource_count:
                    resource_count[resource_type] = 0
                if resource_count[resource_type] < self.max_results_per_type:
                    cleaned_resources.append(resource)
                    resource_count[resource_type] += 1
        else:
            cleaned_resources = unique_resources

        print(f"Resources after limiting: {len(cleaned_resources)}")  #! Remove

        # Limit the number of resources to 20
        if len(cleaned_resources) > 20:
            cleaned_resources = cleaned_resources[:20]

        print(f"Resources after limiting to 20: {len(cleaned_resources)}")  #! Remove

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

        print(
            f"Resources after checking status code: {len(non_error_resources)}"
        )  #! Remove

        return {
            "resources": non_error_resources,
            "topic": resources["topic"],
            "total_resources": len(non_error_resources),
            "model_output": resources["model_output"],
            "generation_time": resources["time_taken"],
            "cleaning_time": round(time.time() - start_time, 2),
            "specific_resources": resources["specific_resources"],
        }


if __name__ == "__main__":
    flr_llm = FindLearningResources(use_llm=True)

    topics = [
        "Deep Learning",
        "Arabic Language",
        "Stock Market Analysis",
        "Human Brain",
    ]

    specific_resources = [
        ["Roadmaps", "Blogs/Articles", "YouTube Videos"],
        ["Roadmaps"],
        ["Blogs/Articles", "YouTube Videos"],
        [],
    ]

    results = flr_llm.find_multiple_resources(topics, specific_resources)

    with open(DEFAULT_PATH + "/test/resources.json", "w") as f:
        json.dump(results, f, indent=4)

    print(
        f"Learning resources for the topics '{topics}' using LLM saved to {DEFAULT_PATH}/test/resources.json"
    )

    for result in results:
        print(
            f"Topic: {result['topic']}, Number of Resources: {len(result['resources'])}"
        )
