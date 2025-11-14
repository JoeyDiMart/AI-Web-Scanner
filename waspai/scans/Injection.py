from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def groupForms(injection_fields: dict) -> tuple[dict, list]:  # helper function to group fields that have the same form id
    form_fields = {}
    standalone_fields = []

    for field in injection_fields:
        form_id = field.get('form_id')

        if form_id != 'N/A':
            if form_id not in form_fields:
                form_fields[form_id] = []
            form_fields[form_id].append(field)

        else:
            standalone_fields.append(field)

    return form_fields, standalone_fields


def standaloneFields():
    pass


def formGroupedFields():
    pass


def main(driver: WebDriver, injection_fields: dict, headers: dict, url: str):

    found_vulnerabilities = False
    num_fields = 0  # len(entry_fields)
    num_successful = 0
    results = {}
    ''' example of results dict
    results = {
        'cookies': (driver.get_cookies())
        'field_name: 'username' example
        'headers': 
        'origin_url': url the field was found in
        'post_url': url to get sent to after injection (driver.current_url) might get used or entry_fields.form_action
        'payload': "whatever was sent in like ' or 1=1"
        'status_code': 201
    }
    '''
    SQL_INJECTION_PAYLOADS = [
        "' OR '1'='1",
        "' OR 1=1--",
        "admin'--",
        "' OR 'a'='a",
        "1' OR '1'='1'--",
        "admin' OR '1'='1'/*",
        "' OR '1'='1' #",
        "' OR '1'='1'--",
    ]
    form_fields, standalone_fields = groupForms(injection_fields)

    return driver, found_vulnerabilities, num_fields, num_successful, results