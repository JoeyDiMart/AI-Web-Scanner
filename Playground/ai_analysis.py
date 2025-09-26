'''
The test program for making an API call with my openai API key
This will read from responses.txt
'''
import os
from openai import OpenAI
from dotenv import load_dotenv


def main():
    load_dotenv("test.env")

    client = OpenAI(api_key=os.getenv("API_KEY"))
    gpt_model = "o3-mini"

    with open("responses.txt", "r", encoding="utf-8") as f:
        text = f.read()

    response = client.responses.create(
        model=gpt_model,
        max_output_tokens=500,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": f'Read this log and summarize:\n {text}'},
                    {"type": "input_text", "text": "Give me a score of how vulnerable this website is where 0 is "
                                                   "Extremely vulnerable and 10 is very secure"}
                ]
            }
        ]
    )
    print(response.output_text)
    open("responses.txt", "w").close()
