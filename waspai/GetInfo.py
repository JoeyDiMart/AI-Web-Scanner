'''
This program gathers the initial cookies, headers, and creates a dictionary of all input fields/buttons
'''
from typing import Tuple
import requests
from bs4 import BeautifulSoup


def getHeaders(response):  # function for filling the headers field
    return response.headers


def getCookies(response):
    return response.cookies.get_dict()


def parseFields(input_fields, response):
    soup = BeautifulSoup(response.text, "html.parser")
    base_url = getattr(response, "url", "") or ""

    form_list = []
    for index, form in enumerate(soup.find_all("form")):  # loop through code for all forms first
        fid = form.get("id") or f"form_{index}"

    return input_fields


def getInput_fields(response, url):
    # AI generated dictionary to show all the fields to look for
    input_fields = {
        "input:text": [],
        "input:password": [],
        "input:hidden": [],  # CSRF tokens, session fields, flags
        "input:file": [],  # file upload testing
        "input:checkbox": [],
        "input:radio": [],
        "textarea": [],
        "select": [],  # include options inside each select record
        "button": [],  # <button> and input[type=submit]
        "anchor": [],  # <a href=...> navigable links
        "form": [],  # forms (action, method, enctype, inputs list)
        "iframe": [],  # third-party frames (important for clickjacking/CSRF)
        "other": []  # anything else worth flagging
    }
    input_fields = parseFields(input_fields, response)

    return input_fields


def main(url: str, session: requests.Session) -> Tuple[dict[str, list[dict[str, str]]], dict[str, str], dict[str, str]]:

    try:
        response = session.get(url, timeout=10)
    except requests.exceptions.ConnectionError:
        print("Connection Error: Failed to connect to URL")
        return {"": [{"": ""}]}, {"": ""}, {"": ""}
    except requests.exceptions.Timeout:
        print("Timeout Error: Server took too long to respond")
        return {"": [{"": ""}]}, {"": ""}, {"": ""}
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"": [{"": ""}]}, {"": ""}, {"": ""}

    headers = getHeaders(response)
    cookies = getCookies(response)
    input_fields = getInput_fields(response, url)


    return input_fields, headers, cookies



