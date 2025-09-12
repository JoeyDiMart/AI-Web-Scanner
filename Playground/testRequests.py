import requests

# 1) A simple GET request
r = requests.get("https://httpbin.org/get")
print("Status code:", r.status_code)    # 200 means OK
print("URL:", r.url)
print("Response body:", r.text[:200], "...\n")   # first 200 chars in the response from the server

# 2) Sending query parameters (?name=Joey&age=21)
params = {"name": "Joey", "age": 21}
r = requests.get("https://httpbin.org/get", params=params)
print("URL with params:", r.url)
print("Response JSON:", r.json(), "\n")

# 3) Sending POST data (like a login form)
data = {"username": "admin", "password": "secret"}
r = requests.post("https://httpbin.org/post", data=data)
print("POST response:", r.json(), "\n")

# 4) Adding custom headers (pretend to be Chrome)
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124"}
r = requests.get("https://httpbin.org/headers", headers=headers)
print("Headers seen by server:", r.json(), "\n")

# 5) Cookies
cookies = {"session": "abc123"}
r = requests.get("https://httpbin.org/cookies", cookies=cookies)
print("Cookies sent:", r.json(), "\n\n")



### Below will be example site
# use localhost:5050    (where dvwa is hosted)