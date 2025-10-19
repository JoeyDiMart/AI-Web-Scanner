'''
This program gathers the initial cookies, headers, and creates a dictionary of all input fields/buttons
'''
from typing import Tuple
import requests
from bs4 import BeautifulSoup


# The global variables
input_fields = {}
headers = []
cookies = []


def getHeaders(response):  # function for filling the headers field
    global headers
    headers = response.headers


def main(url: str) -> Tuple[dict[str, list[str]], dict[str, str], list[str]]:

    try:
        response = requests.get(url, timeout=10)
    except ConnectionError:
        print("Connection Error: Failed to connect to URL")
        return {"": [""]}, {"": ""}, [""]
    except TimeoutError:
        print("Timeout Error: Server took too long to respond")
        return {"": [""]}, {"": ""}, [""]
    except requests.exceptions.RequestException as e:
        print("Request failed: {e}")
        return {"": [""]}, {"": ""}, [""]

    getHeaders(response)


    return input_fields, headers, cookies



