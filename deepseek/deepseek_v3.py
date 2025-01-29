from huggingface_hub import InferenceClient
from dotenv import find_dotenv, dotenv_values
import time

hf_access_token = tavily_api_key = dotenv_values(find_dotenv())["HF_ACCESS_TOKEN"]

client = InferenceClient(provider="together", api_key=hf_access_token)

messages = [
    {
        "role": "user",
        "content": "A box contains 5 red balls and 3 blue balls. Two balls are drawn at random without replacement. What is the probability that the second ball is blue given that the first ball is red?",
    }
]

start = time.time()
stream_v3 = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V3", messages=messages, max_tokens=500, stream=True
)
v3_end = time.time()

stream_r1 = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1", messages=messages, max_tokens=500, stream=True
)
r1_end = time.time()

print("DeepSeek V3")
print()
print("Time taken to get response: ", v3_end - start)
print()
for chunk in stream_v3:
    try:
        print(chunk.choices[0].delta.content, end="")
    except:
        print()
        break

print()
print("DeepSeek R1")
print()
print("Time taken to get response: ", r1_end - v3_end)
print()
for chunk in stream_r1:
    try:
        print(chunk.choices[0].delta.content, end="")
    except:
        print()
        break
