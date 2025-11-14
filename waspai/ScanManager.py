import threading
from .scans import Injection


def broken_access_control(driver, entry_fields, headers, scan_types):
    # print("Broken access started")
    pass


def cryptographic_failure(driver, entry_fields, headers, scan_types):
    # print("cryptographic failure started")
    pass


def injection(driver, injection_fields, headers, scan_types):
    # print("injection started")
    # print(injection_fields)
    Injection.main(driver, injection_fields, headers, scan_types)


def insecure_design(driver, entry_fields, headers, scan_types):
    # print("insecure design started")
    pass


def security_misconfiguration(driver, entry_fields, headers, scan_types):
    # print("security misconfiguration started")
    pass


def vulnerable_and_outdated_components(driver, entry_fields, headers, scan_types):
    # print("vulnerable and outdated components started")
    pass


def identification_and_authentication_failures(driver, entry_fields, headers, scan_types):
    # print("identification and authentication failures started")
    pass


def software_and_data_integrity_failures(driver, entry_fields, headers, scan_types):
    # print("software and data integrity failures started")
    pass


def security_logging_and_monitoring_failures(driver, entry_fields, headers, scan_types):
    # print("security logging and monitoring failures started")
    pass


def server_side_requests_forgery(driver, entry_fields, headers, scan_types):
    # print("server side requests forgery started")
    pass


def main(driver, entry_fields, headers, scan_types):
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
                    args=(driver, temp_fields, headers, scan_types)
                )

    for i in threads:
        threads[i].start()

    for i in threads:
        threads[i].join()

    print(scan_types)
