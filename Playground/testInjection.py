import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def fetchInfo(url: str):
    s = requests.Session()  # Create a session object
    r = s.get(url, allow_redirects=False, timeout=15)  # send a GET request to the given url and go to a different page if asked to redirect
    print(r.text)
    return s, r.text, r.url  # return the session, html, and the url after being redirected


def submitLogin(data, method, url, session):
    headers = {
        "Referer": url,  # make sure this is exactly http://localhost:5050/login.php
        "Origin": "http://localhost:5050",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/140.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    session.cookies.set("security", "low", domain="localhost", path="/")
    print("[DEBUG] Cookies before login:", session.cookies.get_dict())
    print("[DEBUG] Submitting payload:", data)

    if method == "POST":
        r = session.post(url, data=data, allow_redirects=False, timeout=15, headers=headers)
    else:
        r = session.get(url, params=data, allow_redirects=False, timeout=15, headers=headers)
    print("[DEBUG] Submitted payload:", data)

    if r.status_code == 302 and r.headers.get("Location") == "index.php":
        print("✅ Login success")
        return urljoin(url, "index.php")
    else:
        print("❌ Login failed")
        print("r.cookies: ", r.cookies)
        return url


def passLogin(html, url, username, password, session):  # we start off in a login page, this function will get us past this
    USER_KEYS = {"username", "user", "email", "login"}  # take this list to guess the input field and see which is for usernames
    PASS_KEYS = {"password", "pass", "pwd"}  # guess which field is named for password input
    soup = BeautifulSoup(html, "html.parser")  # the html is just text so use this to parse through
    login_form = None

    for form in soup.find_all("form"):  # loop to find the form that sends a password as one of the inputs
        if form.find("input", {"type": "password"}):
            login_form = form  # find the form container that would be sent to log in
            break
    if not login_form:
        raise RuntimeError("No login form with a password input found.")  # couldn't find somewhere to log in here...

    method = (login_form.get("method") or "GET").upper()  # basically see if it's a post or a get request
    action_url = urljoin(url, login_form.get("action") or url)

    data = {}
    for inp in login_form.find_all("input"):
        name = inp.get("name")
        intype = (inp.get("type") or "").lower()
        if not name:
            continue
        val = inp.get("value") or ""

        in_name = name.lower()
        if in_name in USER_KEYS and intype != "submit":
            val = username
        elif intype == "password":
            val = password
        # ✅ include hidden fields like user_token automatically
        data[name] = val
    final_url = submitLogin(data, method, action_url, session)
    return final_url


def main():
    ap = argparse.ArgumentParser(description="Generic login: auto-detect token + submit creds")
    ap.add_argument("url", help="e.g. http://localhost:5050/login.php")
    ap.add_argument("--username", default="admin")
    ap.add_argument("--password", default="password")
    ap.add_argument("--user-field", help="explicit username field name (optional)")
    ap.add_argument("--pass-field", help="explicit password field name (optional)")
    args = ap.parse_args()
    url = args.url

    session, html, url = fetchInfo(url)
    final_url = passLogin(html, url, args.username, args.password, session)


if __name__ == "__main__":
    main()
