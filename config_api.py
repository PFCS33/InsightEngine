import openai
import os

proxy = {
'http': 'http://localhost:7890',
'https': 'http://localhost:7890'
}

openai.proxy = proxy

# update 4/14
api_key = ''