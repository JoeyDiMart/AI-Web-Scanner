from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def main(driver, injection_fields, headers, scan_types):

    found_vulnerabilities = False
    num_fields = 0  # len(entry_fields)
    results = {}
    '''
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
    num_successful = 0

    return driver, found_vulnerabilities, num_fields, num_successful, results