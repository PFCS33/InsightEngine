import openai
import os

proxy = {
'http': 'http://localhost:7890',
'https': 'http://localhost:7890'
}

openai.proxy = proxy

# update 5/7
api_key = ''