'''
This program gathers the initial cookies, headers, and entries (which can be any field that takes user input)
'''
from typing import Tuple, Optional
import requests
from urllib.parse import urljoin, urlparse
import time
from waspai import optimize_info


# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Global Vars
REQUEST_TIMEOUT = 10


def getHeaders(response) -> dict:  # function for filling the headers field
    return dict(response.headers)


def getCookies(response) -> dict:  # fill the cookies field
    return response.cookies.get_dict()


def internalLink(href, url):
    if href.startswith(("javascript:", "mailto:", "tel:")):
        return False
    elif href.startswith("#") or href.startswith("/"):
        return True
    return href.startswith(url)
def buildList(elements, url):
    entries_list = []
    script = """
                    var items = {};
                    for (var i = 0; i < arguments[0].attributes.length; ++i) {
                        items[arguments[0].attributes[i].name] = arguments[0].attributes[i].value;
                    }
                    return items;
                """

    for e in elements:
        entry = {}
        attr = e.parent.execute_script(script, e) or {}
        attr["tag"] = e.tag_name.lower()

        if attr["tag"] == "a":
            href = (e.get_attribute("href") or "").strip().lower()
            if not internalLink(href, url):
                continue

        attr["text"] = (e.text or "").strip()

        try:
            form = e.find_element(By.XPATH, "./ancestor::form")
            attr["form_id"] = form.get_attribute("id") or form.get_attribute("name") or ""
            attr["form_action"] = form.get_attribute("action") or ""
            attr["form_method"] = (form.get_attribute("method") or "get").lower()
        except Exception:
            attr["form_id"] = "N/A"
            attr["form_action"] = "N/A"
            attr["form_method"] = "N/A"

        for k, v in attr.items():
            entry[k] = v
        entries_list.append(entry)

    return entries_list
def renderContent(driver: WebDriver, adaptive_timeout: int) -> tuple[int, int]:
    initial_html = driver.page_source
    initial_len = len(initial_html)
    prev_len = initial_len
    counter = 0

    WebDriverWait(driver, adaptive_timeout).until(  # load DOM before scraping
        lambda d: d.execute_script("return document.readyState === 'complete'")
    )

    for i in range(8):  # take up to 4 seconds to render DOM
        curr_len = len(driver.page_source)

        if curr_len == prev_len:
            counter += 1
        else:
            counter = 0
            prev_len = curr_len
        time.sleep(0.3)
        if counter >= 3:
            break

    dom_change = curr_len - initial_len  # static sites dom change usually 0, dynamic sites usually a lot
    growth_pct = (dom_change / initial_len * 100) if initial_len else 0

    if growth_pct > 20:
        adaptive_timeout = min(20, int(adaptive_timeout * 1.5))  # more time to dynamic pages

        js_roots = ["app-root", "root", "app"]
        for id in js_roots:
            try:
                WebDriverWait(driver, adaptive_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, id))
                )
            except Exception:
                continue
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input | //button | //form | //textarea | //a | //select")
                )
            )
        except Exception:
            print("No changes showing elements")

    else:
        adaptive_timeout = 6  # for static web pages

    time.sleep(1)
    final_len = len(driver.page_source)
    dom_change = final_len - initial_len
    return dom_change, adaptive_timeout
def initDriver() -> WebDriver:  # helper function to start up the chrome driver

    ### dont open a window, don't use GPU, and bypass bot detection ###
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument("--disable-gpu")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.6778.265 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    return driver
def parseEntries(url: str, app_type, adaptive_timeout) -> tuple[list, str, int]:
    driver = initDriver()
    try:
        driver.get(url)
        dom_change, adaptive_timeout = renderContent(driver, adaptive_timeout)

        try:
            WebDriverWait(driver, adaptive_timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input | //textarea | //select | //button | //a | //*[@contenteditable='true']")
                )
            )
        except Exception:
            pass

            # Grab all likely interactive elements including anchors
        elements = driver.find_elements(
            By.XPATH,
            "//input | //textarea | //select | //button | //a | //*[@contenteditable='true']"
        )

        entries_list = buildList(elements, url)
        return entries_list, app_type, dom_change
    finally:
        driver.quit()


def main(url: str, session: requests.Session, app_options, adaptive_timeout: int, scan_map: dict[str,str], app_type="auto") -> (
        Tuple)[list, dict, dict, int, str]:

    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.ConnectionError:
        print("Connection Error: Failed to connect to URL")
        return [], {}, {}, 0, ""
    except requests.exceptions.Timeout:
        print("Timeout Error: Server took too long to respond")
        return [], {}, {}, 0, ""
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return [], {}, {}, 0, ""

    headers = getHeaders(response)
    cookies = getCookies(response)
    entry_fields, app_type, dom_change = parseEntries(url, app_type, adaptive_timeout)
    entry_fields, app_type = optimize_info.main(entry_fields, headers, app_type, dom_change, app_options, scan_map)

    return entry_fields, headers, cookies, adaptive_timeout, app_type
