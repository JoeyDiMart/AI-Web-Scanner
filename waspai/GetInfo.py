'''
This program gathers the initial cookies, headers, and entries (which can be any field that takes user input)
'''
from typing import Tuple, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re  # search for patterns
#from waspai import optimize_info

# Selenium imports


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


def optimizeEntries(entry_fields):
    pass


def findApp_type(response, app_type):
    html = response.text.lower()
    headers = {k.lower(): v.lower() for k, v in response.headers.items()}
    content_type = headers.get("content-type", "")
    script_count = len(re.findall(r"<script", html))
    js_indicators = [
        "reactroot",
        "react-dom",
        "next-data",
        "__next",
        "webpack",
        "vite",
        "vue.js",
        "ng-version",
        "svelte",
        "blazor.webassembly.js",
        "window.__initial_state__",
        "document.createelement('app')",
    ]

    if "application/json" in content_type or html.strip().startswith("{"):  # means it returned JSON
        return app_type, False

    if any(token in html for token in
           js_indicators):  # if the HTML has anything from that list, it means it's dynamic JS-heavy
        return app_type, True

    if script_count > 10:  # random number to count how many scrips are in a webpage
        return app_type, True

    if re.search(r'<script[^>]+src=["\'][^"\']+\.js["\']', html):  # see if a script has something
        return app_type, True

    return app_type, False


def getHeaders(response) -> dict:  # function for filling the headers field
    return dict(response.headers)


def getCookies(response) -> dict:
    return response.cookies.get_dict()


def parseStaticEntries(url, response):
    page_url = getattr(response, "url", "")
    soup = BeautifulSoup(response.text, "html.parser")
    entries: list[dict[str, any]] = []  # start with empty list

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
        # Use classic headless mode for better compatibility
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")

        # If Chrome isn’t found automatically, uncomment the next line:
        # options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        driver_path = ChromeDriverManager().install()
        print(f"[Selenium] Using driver at: {driver_path}")

        driver = webdriver.Chrome(service=ChromeService(driver_path), options=options)
        print(f"[Selenium] Opening {url}")
        driver.get(url)

        # Wait for full document ready state (not just forms)
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Give time for dynamic JS rendering
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "form"))
            )
        except TimeoutException:
            print("[Selenium] No forms found yet – continuing anyway.")

        html = driver.page_source
        driver.quit()

        # Reuse your static parser on the rendered HTML
        entries = parseStaticEntries(url, type("Resp", (object,), {"text": html, "url": url})())
        return entries

    except Exception as e:
        print("[Selenium] Exception during parseJSEntries:")
        traceback.print_exc()
        print("[Selenium] Hint: check that Chrome is installed and ChromeDriver matches Chrome version.")
        return []


def getEntries(url: str, response: requests.Response, app_type: str):
    needs_selenium = NEEDS_SELENIUM.get(app_type, None)  # can be True, False, or None
    static_entries = parseStaticEntries(url, response)

    if needs_selenium is None:
        app_type, needs_selenium = findApp_type(response, app_type)
    if needs_selenium:
        js_entries = parseJSEntries(url)
        combined = {f"{e['form_action']}::{e['input_name']}": e for e in static_entries + js_entries if
                    e.get("input_name")}
        entry_fields = {"inputs": list(combined.values())}
    else:
        entry_fields = {"inputs": static_entries}

    return entry_fields


def main(url: str, session: requests.Session, app_type: str) -> Tuple[
    dict[str, list[dict[str, str]]], dict[str, str], dict[str, str]]:

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
    #entry_fields = optimize_info.main(entry_fields)

    return entry_fields, headers, cookies
