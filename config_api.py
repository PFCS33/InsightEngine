import openai
import os

proxy = {
'http': 'http://localhost:7890',
'https': 'http://localhost:7890'
}

openai.proxy = proxy

# gpt4.0 key
api_key = '--'