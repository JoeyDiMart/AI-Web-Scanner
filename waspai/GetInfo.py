'''
This program gathers the initial cookies, headers, and entries (which can be any field that takes user input)
'''
from typing import Tuple, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, TimeoutException

NEEDS_SELENIUM = {
    "auto": None,
    "static": False,
    "php": False,
    "laravel": False,
    "django": False,
    "flask": False,
    "aspnet": False,
    "dotnet-blazor": True,
    "ruby-on-rails": False,
    "java-spring": False,
    "react": True,
    "nextjs": True,
    "vue": True,
    "nuxt": True,
    "angular": True,
    "svelte": True,
    "wordpress": False,
    "drupal": False,
    "joomla": False,
    "magento": False,
    "shopify": False,
    "api": False,
    "unknown": True,
}

# helper functions
def build_entry(site_url: str,
                form_action: Optional[str],
                form_method: [str],
                form_enctype: [str],
                form_identifier: [str],
                input_name: [str],
                input_id: [str],
                input_type: str,
                input_value: [str],
                snippet: [str],
                source: str,
                extra: Optional[dict[str, any]] = None,
                ) -> dict[str, any]:  # function to create a dict to put into the final entries list
    entry = {
        "site_url": site_url,
        "form_action": urljoin(site_url, form_action or ""),
        "form_method": form_method,
        "form_enctype": form_enctype,
        "form_identifier": form_identifier,
        "input_name": input_name,
        "input_id": input_id,
        "input_type": input_type,
        "input_value": input_value,
        "outer_html_snippet": snippet[:200],
        "source": source,
    }
    if extra:
        entry.update(extra)
    return entry


def findApp_type(url, response, app_type):
    html = response.text.lower()
    headers = {k.lower(): v.lower() for k, v in response.headers.items()}
    print(headers)
    return True


def getHeaders(response) -> dict:  # function for filling the headers field
    return dict(response.headers)


def getCookies(response) -> dict:
    return response.cookies.get_dict()


def parseStaticEntries(url, response):
    page_url = getattr(response, "url", "")
    soup = BeautifulSoup(response.text, "html.parser")
    entries: list[dict[str, any]] = [{"": ""}]

    ####---  Loop through Forms  ---####
    for f_idx, form in enumerate(soup.find_all("form")):
        fid = form.get("id") or form.get("name") or f"form_{f_idx}"  # give a form ID or a name

        action_raw = form.get("action") or ""  # see the action URL for submitting the form
        method = (form.get("method") or "GET").upper()  # see what type of HTTP request is sent
        enctype = form.get("enctype") or "application/x-www-form-urlencoded"  # see encoding type

        # gather hidden fields to attach later if desired
        hidden_map = {}
        for hid in form.find_all("input", {"type": "hidden"}):
            hname = hid.get("name") or hid.get("id")
            if hname:
                hidden_map[hname] = hid.get("value")

        for inp in form.find_all(["input", "textarea", "select", "button"]):  # see if form has elements within
            tag = inp.name
            input_type = inp.get("type") if tag == "input" else tag
            name = inp.get("name")
            iid = inp.get("id")
            value = inp.get("value") or ""

            if tag == "select":  # select has multiple predetermined choices so loop through
                options = []
                for opt in inp.find_all("option"):
                    options.append({"value": opt.get("value"), "text": opt.text})
            else:
                options = None

            outer = str(inp)

            entry = build_entry(
                site_url=page_url,
                form_action=action_raw,
                form_method=method,
                form_enctype=enctype,
                form_identifier=fid,
                input_name=name,
                input_id=iid,
                input_type=(input_type or "text"),
                input_value=value,
                snippet=outer,
                source="static",
                extra={"options": options, "form_hidden_fields": hidden_map if hidden_map else None}
            )
            entries.append(entry)
    return entries


def parseJSEntries(url: str):
    entries = []
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.get(url)

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "form")))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        entries = parseStaticEntries(url, type("Resp", (object,), {"text": driver.page_source, "url": url})())
        driver.quit()

    except (WebDriverException, TimeoutException) as e:
        print(f"Selenium error: {e}")
        return []

    return entries


def getEntries(url: str, response: requests.Response, app_type: str):
    needs_selenium = NEEDS_SELENIUM.get(app_type, None)  # can be True, False, or None
    static_entries = parseStaticEntries(url, response)

    if NEEDS_SELENIUM[app_type] is None:
        needs_selenium = findApp_type(url, response, app_type)
    if needs_selenium:
        js_entries = parseJSEntries(url)
        combined = {f"{e['form_action']}::{e['input_name']}": e for e in static_entries + js_entries if e.get("input_name")}
        entry_fields = {"inputs": list(combined.values())}
    else:
        entry_fields = {"inputs": static_entries}

    return entry_fields


def main(url: str, session: requests.Session, app_type: str) -> Tuple[dict[str, list[dict[str, str]]], dict[str, str], dict[str, str]]:
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
    entry_fields = getEntries(url, response, app_type)

    return entry_fields, headers, cookies
