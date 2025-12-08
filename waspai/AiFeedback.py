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
    4. For each category with vulnerabilities, provide:
    • Bullet-pointed remediation recommendations with specific, actionable steps
    • Prioritized by severity (address critical issues first)
    • References to relevant security standards (OWASP, CWE) where applicable
    
    **Data to Analyze:**
    {json.dumps(scan_results)}
    
    
    **Required JSON Output Format:**
    {{
    "overall_score": <number 0-100>,
    "categories": [
        {{
            "category_id": "A01",
            "category_name": "Broken Access Control",
            "score": <number>,
            "max_score": <number>,
            "vulnerabilities_found": <number>,
            "severity": "critical|high|medium|low|none",
            "remediation": [
                {{
                    "priority": "critical|high|medium|low",
                    "issue": "Brief description of the vulnerability",
                    "recommendation": "Specific actionable fix",
                    "reference": "OWASP/CWE reference if applicable"
                }}
            ]
        }}
        ],
        "summary": "Brief overall security assessment",
        "critical_findings": <number of critical issues>,
        "high_findings": <number of high severity issues>
    }}

**Important:**
- Only analyze categories present in the scan results
- Be specific in remediation steps (include code examples, configuration changes, or tools)
- Prioritize critical issues first in remediation arrays
- Reference specific OWASP guidelines or CWE numbers where applicable
    """

    try:
        response = client.chat.completions.create(
            model=gpt_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a security analysis assistant. You ONLY output valid JSON. No markdown, no explanations, just pure JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        message = response.choices[0].message

        # Parse the JSON response
        if hasattr(message, "parsed"):
            feedback = message.parsed
        else:
            try:
                feedback = json.loads(message.content)
            except json.JSONDecodeError as je:
                print(f"[!] JSON parsing error: {je}")
                print(f"[!] Raw content: {message.content[:500]}")
                feedback = {
                    "error": "Failed to parse JSON response",
                    "overall_score": 0,
                    "categories": []
                }

        return feedback

    except Exception as e:
        print(f"[!] OpenAI API error: {e}")
        return {
            "error": str(e),
            "overall_score": 0,
            "categories": []
        }


NOTE THIS TODO

- take in the app type parameter to specify the the recommendation, print a little nicer as well