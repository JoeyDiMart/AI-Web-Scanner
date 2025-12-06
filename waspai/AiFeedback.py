import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
OPENAI_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=OPENAI_KEY)
gpt_model = "gpt-4o-mini-2024-07-18"

OWASP_TOP_10 = {
    "A01": "Broken Access Control",
    "A02": "Security Misconfiguration",
    "A03": "Software Supply Chain Failures",
    "A04": "Cryptographic Failures",
    "A05": "Injection",
    "A06": "Insecure Design",
    "A07": "Authentication Failures",
    "A08": "Software or Data Integrity Failures",
    "A09": "Logging and Alerting Failures",
    "A10": "Mishandling of Exceptional Conditions"
}


def findPPS():
    # going to return find points per scan
    # maybe rank OWASP #1 higher / more weight than A10 ?
    pass


# scan map for -scan i will only be { i: injection }
def main(scan_map, scan_results):
    prompt = f"""
    You are an expert web fingerprinting and security analysis assistant.
            
    INSTRUCTIONS:
    1. For each category tested, evaluate the severity and quantity of vulnerabilities found
    2. Assign a score for that category (0 to X  points):
    - Full points: No vulnerabilities found
   - Partial points: Minor or low-severity issues
   - Zero points: Critical or high-severity vulnerabilities
3. Sum all category scores to get the final security rating (0-100)
    
    
    **Data to Analyze:**
    {json.dumps(scan_results)}
    
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
    except Exception as e:
        print(f"[!] OpenAI failed: {e}")

