from openai import OpenAI
import os

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"

client = OpenAI(
    base_url='https://api.openai-proxy.org/v1',
    api_key='',
)