import openai
import os

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"


openai.api_key = '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'

def get_completion_from_messages(messages, model="gpt-4", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
#     print(str(response.choices[0].message))
    return response.choices[0].message["content"]


if __name__ == '__main__':

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Which vitamin is supplied from only animal source:A.Vitamin C B. Vitamin B7 C.Vitamin B12 D. Vitamin D"},
    ]
    response = get_completion_from_messages(messages, temperature=0)
    print(response)

