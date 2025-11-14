import threading

from selenium.webdriver.chrome.webdriver import WebDriver

from .scans import Injection


def broken_access_control(driver: WebDriver, entry_fields: dict, headers: dict, url: str):
    # print("Broken access started")
    pass


def cryptographic_failure(driver: WebDriver, entry_fields: dict, headers: dict, url: str):
    # print("cryptographic failure started")
    pass


def injection(driver: WebDriver, injection_fields: dict, headers: dict, url: str):
    # print("injection started")
    # print(injection_fields)
    Injection.main(driver, injection_fields, headers, url)


def insecure_design(driver: WebDriver, entry_fields: dict, headers: dict, url: str):
    # print("insecure design started")
    pass


def security_misconfiguration(driver: WebDriver, entry_fields: dict, headers: dict, url: str):
    # print("security misconfiguration started")
    pass


def vulnerable_and_outdated_components(driver: WebDriver, entry_fields: dict, headers: dict, url: str):
    # print("vulnerable and outdated components started")
    pass


def identification_and_authentication_failures(driver: WebDriver, entry_fields: dict, headers: dict, url: str):
    # print("identification and authentication failures started")
    pass


def software_and_data_integrity_failures(driver: WebDriver, entry_fields: dict, headers: dict, url: str):
    # print("software and data integrity failures started")
    pass


def security_logging_and_monitoring_failures(driver: WebDriver, entry_fields: dict, headers: dict, url: str):
    # print("security logging and monitoring failures started")
    pass


def server_side_requests_forgery(driver: WebDriver, entry_fields: dict, headers: dict, url: str):
    # print("server side requests forgery started")
    pass


def main(driver: WebDriver, entry_fields: dict, headers: dict, scan_types: dict, url: str):
    threads = {}
    function_map = {
        "b": broken_access_control,
        "c": cryptographic_failure,
        "i": injection,
        "d": insecure_design,
        "m": security_misconfiguration,
        "v": vulnerable_and_outdated_components,
        "a": identification_and_authentication_failures,
        "s": software_and_data_integrity_failures,
        "l": security_logging_and_monitoring_failures,
        "r": server_side_requests_forgery
    }

    for i, name in enumerate(scan_types):
        if scan_types[name] == 0:
            temp_fields = []
            for field in entry_fields:
                if name in field['possible_scan']:
                    temp_fields.append(field)

            if temp_fields:
                threads[name] = threading.Thread(
                    target=function_map[name],
                    args=(driver, temp_fields, headers, scan_types, url)
                )

    for i in threads:
        threads[i].start()

    for i in threads:
        threads[i].join()

    print(scan_types)
