import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# grab
def fetchInfo(url: str):
    s = requests.Session()  # Create a session object
    r = s.get(url, allow_redirects=True, timeout=15)  # send a GET request to the given url and go to a different page if asked to redirect

    return s, r.text, r.url  # return the session, html, and the url after being redirected


def submitLogin(data, method, url, session):
    headers = {
        "Referer": url,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    if method == "POST":
        r = session.post(url, data=data, allow_redirects=False, timeout=15, headers=headers)
    else:
        r = session.get(url, params=data, allow_redirects=True, timeout=15, headers=headers)

    redirect_url = urljoin(url, r.headers["Location"])
    r = session.get(redirect_url, timeout=15)
    return r.url
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
    for inp in login_form.find_all("input"):  # loop to find the input fields for username and passwords
        name = inp.get("name")
        intype = (inp.get("type") or "").lower()
        if not name:
            continue
        val = inp.get("value") or ""
        in_name = name.lower()
        if in_name in USER_KEYS and intype != "submit":
            val = username
        elif (inp.get("type") or "").lower() == "password":
            val = password
        data[name] = val
    final_url = submitLogin(data, method, action_url, session)
    print(final_url)
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
