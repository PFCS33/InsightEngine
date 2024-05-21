import openai
import os
import config_api

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"

openai.api_key = config_api.api_key


def get_completion_from_messages(messages, model="gpt-4o", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    #     print(str(response.choices[0].message))
    return response.choices[0].message["content"]


if __name__ == '__main__':
    nl_query = "Show all the ranks and the number of male and female faculty for each rank in a bar chart."
    database_name = "activity_1"
    index = "11"

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",
         "content": "Which vitamin is supplied from only animal source:A.Vitamin C B. Vitamin B7 C.Vitamin B12 D. Vitamin D"},
    ]
    response = get_completion_from_messages(messages, temperature=0)
    print(response)
