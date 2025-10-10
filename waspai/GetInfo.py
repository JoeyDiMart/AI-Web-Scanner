'''

'''

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fillFields(url: str, driver: ) -> dict[str, list[str]]:
    fields_dict = {
        "input": [],
        "button": [],
        "textarea": [],
        "select": [],
        "a": [],
    }



    driver.get(url)

    return fields_dict

def main(url):
    driver = webdriver.Chrome()
    input_fields, headers, cookies = fillFields(url, driver), "hello", "hey"
    return input_fields, headers, cookies
    driver.quit()
