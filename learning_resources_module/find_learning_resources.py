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
import random
from pprint import pprint

DEFAULT_PATH = os.path.dirname(__file__)

random.seed(time.time())


class FindLearningResources:
    def __init__(
        self,
        use_llm: bool = True,
        max_results_per_type: int = 5,
        check_status_code: bool = False,
        clean_resources: bool = True,
        confidence_threshold: int = 80,
    ):
        """
        Initialize the Tavily API and Google Chat API

        Args:
            use_llm (bool): Whether to use the LLM to generate responses. Default is True.
            max_results_per_type (int): The maximum number of results to return for each resource type. Default is 5.
            check_status_code (bool): Whether to check the status code of the resources. Default is False.
            clean_resources (bool): Whether to clean the resources. Default is True.
            confidence_threshold (int): The confidence threshold for the resources. Default is 80.

        Returns:
            None
        """

        # Set the parameters for the class
        self.use_llm = use_llm
        self.max_results_per_type = max_results_per_type
        self.check_status_code = check_status_code
        self.clean_resources = clean_resources
        self.confidence_threshold = confidence_threshold / 100

        # Load API keys from .env file
        self.tavily_api_key = dotenv_values(find_dotenv())["TAVILY_API_KEY"]

        if self.use_llm:
            self.gemini_api_key = dotenv_values(find_dotenv())["GEMINI_API_KEY"]

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
                exclude_domains=[],
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

        self.all_resources = [
            {
                "name": "Roadmaps",
                "llm_name": "Roadmaps",
                "tavily_name": "Learning Roadmaps",
                "is_default": False,
                "is_image": False,
            },
            {
                "name": "Blogs",
                "llm_name": "Blogs/Articles",
                "tavily_name": "Learning Blogs",
                "is_default": True,
                "is_image": False,
            },
            {
                "name": "Articles",
                "llm_name": "Blogs/Articles",
                "tavily_name": "Learning Articles",
                "is_default": True,
                "is_image": False,
            },
            {
                "name": "YouTube Videos",
                "llm_name": "YouTube Videos",
                "tavily_name": "Learning YouTube Videos",
                "is_default": True,
                "is_image": False,
            },
            {
                "name": "Scientific Papers",
                "llm_name": "Scientific Papers",
                "tavily_name": "Scientific Papers",
                "is_default": False,
                "is_image": False,
            },
            {
                "name": "Courses",
                "llm_name": "Courses",
                "tavily_name": "Learning Courses",
                "is_default": True,
                "is_image": False,
            },
            {
                "name": "Figures",
                "llm_name": "Images",
                "tavily_name": "Learning Figures",
                "is_default": True,
                "is_image": True,
            },
            {
                "name": "Diagrams",
                "llm_name": "Images",
                "tavily_name": "Learning Diagrams",
                "is_default": True,
                "is_image": True,
            },
            {
                "name": "Charts",
                "llm_name": "Images",
                "tavily_name": "Learning Charts",
                "is_default": False,
                "is_image": True,
            },
            {
                "name": "Infographics",
                "llm_name": "Images",
                "tavily_name": "Learning Infographics",
                "is_default": False,
                "is_image": True,
            },
            {
                "name": "Images",
                "llm_name": "Images",
                "tavily_name": "Learning Images",
                "is_default": True,
                "is_image": True,
            },
            {
                "name": "Communities",
                "llm_name": "Communities/Forums",
                "tavily_name": "Communities",
                "is_default": True,
                "is_image": False,
            },
            {
                "name": "Forums",
                "llm_name": "Communities/Forums",
                "tavily_name": "Forums",
                "is_default": False,
                "is_image": False,
            },
            {
                "name": "Code Repositories",
                "llm_name": "Code Repositories",
                "tavily_name": "Code Repositories",
                "is_default": False,
                "is_image": False,
            },
            {
                "name": "Slides",
                "llm_name": "Slides/Presentations",
                "tavily_name": "Learning Slides",
                "is_default": False,
                "is_image": False,
            },
            {
                "name": "Presentations",
                "llm_name": "Slides/Presentations",
                "tavily_name": "Learning Presentations",
                "is_default": True,
                "is_image": False,
            },
            {
                "name": "Books",
                "llm_name": "Books",
                "tavily_name": "Learning Books",
                "is_default": True,
                "is_image": False,
            },
            {
                "name": "Webinars",
                "llm_name": "Webinars",
                "tavily_name": "Learning Webinars",
                "is_default": False,
                "is_image": False,
            },
            {
                "name": "Case Studies",
                "llm_name": "Case Studies",
                "tavily_name": "Case Studies",
                "is_default": False,
                "is_image": False,
            },
            {
                "name": "Real-world Applications",
                "llm_name": "Real-world Applications",
                "tavily_name": "Real-world Applications",
                "is_default": False,
                "is_image": False,
            },
            {
                "name": "Examples",
                "llm_name": "Examples",
                "tavily_name": "Examples",
                "is_default": True,
                "is_image": False,
            },
        ]

        # Initialize the prompt or resources
        if self.use_llm:
            self.prompt = self._init_prompt()

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
    - Real-world Applications: Practical use cases or industry applications.
    - Examples: Sample code, projects, or exercises.

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

        # Lowercase the specific resources
        if specific_resources is not None or specific_resources != []:
            specific_resources = [resource.lower() for resource in specific_resources]

        if self.use_llm:
            # If specific resources are not provided, use the default resources
            if specific_resources is None or specific_resources == []:
                specific_resources = [
                    resource["llm_name"].lower()
                    for resource in self.all_resources
                    if resource["is_default"]
                ]

                specific_resources_names = [
                    resource["name"]
                    for resource in self.all_resources
                    if resource["is_default"]
                ]

            # Check if specific resources are provided
            else:
                specific_resources = [
                    resource["llm_name"].lower()
                    for resource in self.all_resources
                    if resource["name"].lower() in specific_resources
                ]

                specific_resources_names = [
                    resource["name"]
                    for resource in self.all_resources
                    if resource["name"].lower() in specific_resources
                ]

            # Remove duplicates
            specific_resources = list(set(specific_resources))

            # Generate the input for the LLM
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
            result["specific_resources_names"] = specific_resources_names
            result["specific_resources"] = specific_resources
            if self.clean_resources:
                return self.clean_llm_resources(result)
            else:
                result["cleaning_time"] = 0
                return result

        else:
            # If specific resources are not provided, use the default resources
            if specific_resources is None or specific_resources == []:
                specific_resources_dict = [
                    {
                        "tavily_name": resource["tavily_name"],
                        "is_image": resource["is_image"],
                    }
                    for resource in self.all_resources
                    if resource["is_default"]
                ]
                specific_resources_names = [
                    resource["name"]
                    for resource in self.all_resources
                    if resource["is_default"]
                ]

            # Check if specific resources are provided
            else:
                specific_resources_dict = [
                    {
                        "tavily_name": resource["tavily_name"],
                        "is_image": resource["is_image"],
                    }
                    for resource in self.all_resources
                    if resource["name"].lower() in specific_resources
                ]

                specific_resources_names = [
                    resource["name"]
                    for resource in self.all_resources
                    if resource["name"] in specific_resources
                ]

            # Remove duplicates from the dictionary
            specific_resources_dict = [
                dict(t) for t in {tuple(d.items()) for d in specific_resources_dict}
            ]

            is_image = [resource["is_image"] for resource in specific_resources_dict]
            specific_resources = [
                resource["tavily_name"] for resource in specific_resources_dict
            ]

            # Initialize the list of resources
            resources = []

            # Find resources using the Tavily API
            start_time = time.time()
            for is_image, resource in zip(is_image, specific_resources):
                if is_image:
                    try:
                        results = self.tavily.search(
                            query=f"{topic} {resource}",
                            search_depth="advanced",
                            max_results=random.randint(1, 3),
                            include_images=True,
                            include_answer=False,
                            include_image_descriptions=True,
                            include_raw_content=False,
                            exclude_domains=[],
                        )
                    except Exception as e:
                        results = {"error": str(e)}
                else:
                    try:
                        results = self.tavily.search(
                            query=f"{topic} {resource}",
                            search_depth="advanced",
                            max_results=random.randint(1, 3),
                            include_images=False,
                            include_answer=False,
                            include_image_descriptions=False,
                            include_raw_content=False,
                            exclude_domains=[],
                        )
                    except Exception as e:
                        results = {"error": str(e)}

                if not is_image:
                    for result in results["results"]:
                        resources.append(
                            {
                                "title": result["title"],
                                "url": result["url"],
                                "type": resource,
                                "score": result["score"],
                            }
                        )
                else:
                    for result in results["images"]:
                        resources.append(
                            {
                                "title": result["description"],
                                "url": result["url"],
                                "type": resource,
                                "score": 100,
                            }
                        )

            results_dict = {
                "resources": resources,
                "topic": topic,
                "total_resources": len(resources),
                "model_output": f"Learning resources found for the topic '{topic}', results have been sent to Telegram and B.E.M.O app.",
                "generation_time": round(time.time() - start_time, 2),
                "cleaning_time": 0,
                "specific_resources": specific_resources_names,
            }

            if self.clean_resources:
                return self.clean_non_llm_resources(results_dict)
            else:
                return results_dict

    def find_multiple_resources(
        self, topics: list, specific_resources: list = [[]]
    ) -> list:
        """
        Find learning resources for the given topics

        Args:
            topics (list): The topics for which to find learning resources
            specific_resources (list): The specific types of resources to include for each topic. Default is [[]].

        Returns:
            list: The learning resources found for the given topics
        """

        if len(specific_resources) != len(topics):
            return {
                "error": "The number of specific resources must match the number of topics."
            }

        results = []
        for topic, specific_resource in zip(topics, specific_resources):
            results.append(self.find_resources(topic, specific_resource))

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
            and resource["title"] is not None
            and resource["url"] is not None
            and resource["type"] is not None
        ]

        # Limit the number of resources for each type to the maximum allowed
        if len(resources["specific_resources"]) > 2:
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

        # Remove the resources that give a status code other than 200
        if self.check_status_code:
            non_error_resources = []
            for resource in cleaned_resources:
                url = resource["url"]
                try:
                    response = requests.request("HEAD", url)
                except:
                    status_code = 200
                status_code = response.status_code
                if status_code in allowed_status_codes:
                    non_error_resources.append(resource)
        else:
            non_error_resources = cleaned_resources

        # Limit the number of resources to 20
        if len(non_error_resources) > 20:
            non_error_resources = non_error_resources[:20]

        # Shuffle the list of resources
        non_error_resources = random.sample(
            non_error_resources, len(non_error_resources)
        )

        # Remove all charachters that are not ASCII from the title
        for resource in non_error_resources:
            resource["title"] = "".join(
                char for char in resource["title"] if ord(char) < 128
            )

        return {
            "resources": non_error_resources,
            "topic": resources["topic"],
            "total_resources": len(non_error_resources),
            "model_output": resources["model_output"],
            "generation_time": resources["time_taken"],
            "cleaning_time": round(time.time() - start_time, 2),
            "specific_resources": resources["specific_resources_names"],
        }

    def clean_non_llm_resources(self, resources: dict) -> dict:
        """
        Clean the learning resources generated by the Tavily API

        Args:
            resources (dict): The learning resources generated by the Tavily API

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
            and resource["title"] is not None
            and resource["url"] is not None
            and resource["type"] is not None
        ]

        # Limit the number of resources for each type to the maximum allowed
        if len(resources["specific_resources"]) > 2:
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

        # Remove the resources that give have a score less than 80
        confidence_resources = []
        for resource in cleaned_resources:
            if resource["score"] >= self.confidence_threshold:
                confidence_resources.append(
                    {
                        "title": resource["title"],
                        "url": resource["url"],
                        "type": resource["type"],
                    }
                )

        # Remove the resources that give a status code other than 200
        if self.check_status_code:
            non_error_resources = []
            for resource in confidence_resources:
                url = resource["url"]
                try:
                    response = requests.request("HEAD", url)
                except:
                    status_code = 200
                status_code = response.status_code
                if status_code in allowed_status_codes:
                    non_error_resources.append(resource)

        else:
            non_error_resources = confidence_resources

        # Shuffle the list of resources
        non_error_resources = random.sample(
            non_error_resources, len(non_error_resources)
        )

        # Limit the number of resources to 20
        if len(non_error_resources) > 20:
            non_error_resources = non_error_resources[:20]

        # Remove all charachters that are not ASCII from the title
        for resource in non_error_resources:
            resource["title"] = "".join(
                char for char in resource["title"] if ord(char) < 128
            )

        return {
            "resources": non_error_resources,
            "topic": resources["topic"],
            "total_resources": len(non_error_resources),
            "model_output": resources["model_output"],
            "generation_time": resources["generation_time"],
            "cleaning_time": round(time.time() - start_time, 2),
            "specific_resources": resources["specific_resources"],
        }


if __name__ == "__main__":
    flr_llm = FindLearningResources(use_llm=False)

    # Show the learning resources names
    names = [resource["name"] for resource in flr_llm.all_resources]
    print("Default Learning Resources: ")
    print(names)

    topics = [
        "Arabic Language",
        "Stock Market Analysis",
        "Human Brain",
        "Deep Learning",
    ]

    specific_resources = [
        ["Roadmaps", "YouTube Videos", "Courses"],
        ["Images", "Infographics", "Diagrams", "Charts", "Figures"],
        ["Scientific Papers", "Books", "Webinars", "Real-world Applications"],
        [],
    ]

    results = flr_llm.find_multiple_resources(topics, specific_resources)

    with open(DEFAULT_PATH + "/test/resources.json", "w") as f:
        json.dump(results, f, indent=4)

    print(
        f"Learning resources for the topics '{topics}' using LLM saved to {DEFAULT_PATH}/test/resources.json"
    )

    for result in results:
        try:
            print(
                f"Topic: {result['topic']}, Number of Resources: {len(result['resources'])}"
            )
        except:
            print("Error")
