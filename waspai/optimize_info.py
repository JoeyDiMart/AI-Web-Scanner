import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
OPENAI_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=OPENAI_KEY)
gpt_model = "gpt-4o-mini-2024-07-18"


def optimize(entry_fields):

    return_structure = {
        "name" : "",
        "id" : "",
        "form_action" : "",
        "method" : "",
        "enctype" : "",
        "input_value" : "",
        "form_hidden_fields" : "",
        "classification" : "",      # password, username, csrf, email, textarea, submit, hidden, other
        "suggested_tests" : [],  # simple test values
        "owasp_tags" : []           # OWASP categories like ["injection","xss"]
    }

    sending_structure = []

    prompt = (
        "enter prompt here"
    )

    '''
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a JSON formatting assistant."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    '''

    return entry_fields


def main(entry_fields):
    return optimize(entry_fields)

