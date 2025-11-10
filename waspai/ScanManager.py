import threading


def broken_access_control(scan_types, name):
    print("Broken access started")
    scan_types[name] = 1


def cryptographic_failure(scan_types, name):
    print("cryptographic failure started")
    scan_types[name] = 1


def injection(scan_types, name):
    print("injection started")
    scan_types[name] = 1


def insecure_design(scan_types, name):
    print("insecure design started")
    scan_types[name] = 1


def security_misconfiguration(scan_types, name):
    print("security misconfiguration started")
    scan_types[name] = 1


def vulnerable_and_outdated_components(scan_types, name):
    print("vulnerable and outdated components started")
    scan_types[name] = 1


def identification_and_authentication_failures(scan_types, name):
    print("identification and authentication failures started")
    scan_types[name] = 1


def software_and_data_integrity_failures(scan_types, name):
    print("software and data integrity failures started")
    scan_types[name] = 1


def security_logging_and_monitoring_failures(scan_types, name):
    print("security logging and monitoring failures started")
    scan_types[name] = 1


def server_side_requests_forgery(scan_types, name):
    print("server side requests forgery started")
    scan_types[name] = 1


def main(scan_types):
    thread_names = [
        "t_b", "t_c", "t_i", "t_d", "t_m", "t_v", "t_a", "t_s", "t_l", "t_r"
    ]
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
            if scan_types[name] == 0:
                threads[thread_names[i]] = threading.Thread(
                    target=function_map[name],
                    args=(scan_types, name)
                )

    for i in threads:
        threads[i].start()

    for i in threads:
        threads[i].join()

    print(scan_types)
