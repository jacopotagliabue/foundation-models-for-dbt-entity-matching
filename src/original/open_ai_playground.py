"""
    Minimal code example for a OpenAI request using Python (pure API, no wrapper)
"""

import requests
import json
import time
import os


start = time.time()
url = 'https://api.openai.com/v1/completions'
data =  {
        "model": "text-davinci-002",
        "prompt": "What is the capital of France?", 
        "temperature": 0, 
        "max_tokens": 20
        }
payload = json.dumps(data)
headers = { 
    'content-type': 'application/json', 
    "Authorization": "Bearer {}".format(os.environ['API_KEY'])
    }
r = requests.post(url, data=payload, headers=headers)
print(time.time() - start)
print(json.loads(r.text)["choices"][0]['text'].strip())
