import os
from dotenv import load_dotenv
from openai import OpenAI
import json


load_dotenv()
OPENAI_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=OPENAI_KEY)
gpt_model = "gpt-4o-mini-2024-07-18"

SHORT_FLAG_MAP: dict[str, str] = {
    "b": "broken_access_control",  # b = Broken access
    "c": "cryptographic_failure",  # c = Cryptographic
    "i": "injection",  # i = injection
    "d": "insecure_design",  # d = Design
    "m": "security_misconfiguration",  # m = misconfig
    "v": "vulnerable_and_outdated_components",  # v = vulnerable components
    "a": "identification_and_authentication_failures",  # a = auth / identification
    "s": "software_and_data_integrity_failures",  # S = Software integrity
    "l": "security_logging_and_monitoring_failures",  # l = logging
    "r": "server_side_requests_forgery"  # r = request forgery (SSRF)
}


def optimize(entry_fields, headers, app_type, dom_change, app_options):
    app_options.remove("auto")

    if app_type == "auto":
        prompt = f"""
            You are an expert web fingerprinting and security analysis assistant.
            
            **Your Tasks:**
            1. Determine which web framework/platform the site is most likely built with (choose ONE from app_options)
            2. Filter entry_fields to remove fields that CANNOT be scanned for OWASP Top 10 vulnerabilities
            3. For each remaining field, add a "possible_scan" key with a list of vulnerability short codes

            **Data to Analyze:**
            Entry Fields (input elements from the web page):
            {json.dumps(entry_fields, indent=2)}

            HTTP Headers:
            {json.dumps(headers, indent=2)}

            DOM Change Metric: 
            {dom_change}

            Available App Options (choose ONE):
            {json.dumps(app_options, indent=2)}
            
            **Vulnerability Short Codes:**
            {json.dumps(SHORT_FLAG_MAP, indent=2)}
            
            **Filtering Rules:**
            KEEP fields that can be tested:
            - Text inputs, textareas, search fields → injection (i)
            - Password fields, login forms → auth failures (a)
            - File upload fields → injection (i), insecure design (d), SSRF (r)
            - Forms with POST/PUT/DELETE → broken access control (b)
            - Hidden fields with tokens/IDs → cryptographic failure (c)
            - URL/endpoint inputs → SSRF (r), injection (i)
            
            REMOVE fields that cannot be scanned:
            - Plain navigation links without parameters
            - Disabled or readonly fields
            - Cancel/close buttons without forms
            - Static display elements
            - Pure CSS/JavaScript decorative elements
            
            **Response Format (valid JSON only):**
            {{
              "app_type": "one option from app_options list",
              "entry_fields": [
                {{
                  ...keep all original field data...,
                  "possible_scan": ["i", "a", "b"]
                }}
              ],
            }}

            Return ONLY the JSON object, nothing else.
            
            """

    else:
        prompt = f"""
            You are an expert web fingerprinting and security analysis assistant.
            
            **Your Tasks:**
            1. Filter entry_fields to remove fields that CANNOT be scanned for OWASP Top 10 vulnerabilities
            2. For each remaining field, add a "possible_scan" key with a list of vulnerability short codes

            **Data to Analyze:**
            Entry Fields (input elements from the web page):
            {json.dumps(entry_fields, indent=2)}

            Known App type:
            {json.dumps(app_type, indent=2)}
            
            **Vulnerability Short Codes:**
            {json.dumps(SHORT_FLAG_MAP, indent=2)}
            
            **Filtering Rules:**
            KEEP fields that can be tested:
            - Text inputs, textareas, search fields → injection (i)
            - Password fields, login forms → auth failures (a)
            - File upload fields → injection (i), insecure design (d), SSRF (r)
            - Forms with POST/PUT/DELETE → broken access control (b)
            - Hidden fields with tokens/IDs → cryptographic failure (c)
            - URL/endpoint inputs → SSRF (r), injection (i)
            
            REMOVE fields that cannot be scanned:
            - Plain navigation links without parameters
            - Disabled or readonly fields
            - Cancel/close buttons without forms
            - Static display elements
            - Pure CSS/JavaScript decorative elements
            
            **Response Format (valid JSON only):**
            {{
              "entry_fields": [
                {{
                  ...keep all original field data...,
                  "possible_scan": ["i", "a", "b"]
                }}
              ],
            }}

            Return ONLY the JSON object, nothing else.
            
            """

    try:
        response = client.chat.completions.create(
            model=gpt_model,
            messages=[
                {"role": "system", "content": "You are a JSON-only assistant that outputs nothing except valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        message = response.choices[0].message
        if hasattr(message, "parsed"):
            model_json = message.parsed
        else:
            try:
                model_json = json.loads(message.content)
            except Exception:
                print("[!] Model returned non-JSON output.")
                model_json = {}

        if app_type == "auto":
            app_type = model_json.get("app_type", "unknown")

        entry_fields = model_json.get("entry_fields", entry_fields)

    except Exception as e:
        print(f"[!] OpenAI failed: {e}")
        app_type = app_type or "unknown"

    return entry_fields, app_type


def main(entry_fields, headers, app_type, dom_change, app_options):
    entry_fields, app_type = optimize(entry_fields, headers, app_type, dom_change, app_options)
    return entry_fields, app_type
