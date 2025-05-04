from openai import OpenAI # openai version 1.1.1
from .functions import encode_image
import requests
import os
from dotenv import load_dotenv
load_dotenv()
aux_key = os.environ["OPEN_AI"]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {aux_key}"
}

def get_gpt_response (path, prompt, model_name):
    base64_image = encode_image(path)
    payload = {
        "model": model_name,
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": prompt
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print (response.json())
    return response.json()