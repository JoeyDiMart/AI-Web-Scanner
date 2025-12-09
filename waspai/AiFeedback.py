import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
OPENAI_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=OPENAI_KEY)
gpt_model = "gpt-4o-mini-2024-07-18"

# OWASP Top 10 2021 - DO NOT CHANGE ORDER OR ABBREVIATIONS
OWASP_TOP_10 = {
    "A01": "Broken Access Control",
    "A02": "Cryptographic Failures",
    "A03": "Injection",
    "A04": "Insecure Design",
    "A05": "Security Misconfiguration",
    "A06": "Vulnerable and Outdated Components",
    "A07": "Identification and Authentication Failures",
    "A08": "Software and Data Integrity Failures",
    "A09": "Security Logging and Monitoring Failures",
    "A10": "Server-Side Request Forgery (SSRF)"
}

# Weighted scoring based on OWASP severity ratings
OWASP_WEIGHTS = {
    "A01": 12,  # Broken Access Control - highest priority
    "A03": 12,  # Injection
    "A07": 11,  # Authentication Failures
    "A02": 10,  # Cryptographic Failures
    "A05": 10,  # Security Misconfiguration
    "A04": 9,  # Insecure Design
    "A08": 9,  # Data Integrity Failures
    "A06": 9,  # Vulnerable Components
    "A09": 9,  # Logging Failures
    "A10": 9  # SSRF
}

# Mapping from WaspAI scan codes to OWASP codes (matching your short_flag_map)
SCAN_CODE_TO_OWASP = {
    'b': 'A01',  # broken_access_control
    'c': 'A02',  # cryptographic_failure
    'i': 'A03',  # injection
    'd': 'A04',  # insecure_design
    'm': 'A05',  # security_misconfiguration
    'v': 'A06',  # vulnerable_and_outdated_components
    'a': 'A07',  # identification_and_authentication_failures
    's': 'A08',  # software_and_data_integrity_failures
    'l': 'A09',  # security_logging_and_monitoring_failures
    'r': 'A10',  # server_side_requests_forgery
}


def normalize_scan_codes(scan_map, scan_results):
    """
    Convert WaspAI scan codes (like 'i') to OWASP codes (like 'A03')

    Args:
        scan_map: Original scan map with codes like {'i': 'injection'}
        scan_results: Original scan results with codes like {'i': {...}}

    Returns:
        Tuple of (normalized_map, normalized_results) with OWASP codes
    """
    normalized_map = {}
    normalized_results = {}

    for code, name in scan_map.items():
        # Convert scan code to OWASP code
        owasp_code = SCAN_CODE_TO_OWASP.get(code, code)
        normalized_map[owasp_code] = OWASP_TOP_10.get(owasp_code, name)

        # Transfer results to new key
        if code in scan_results:
            normalized_results[owasp_code] = scan_results[code]

    return normalized_map, normalized_results


def get_tech_specific_guidance(app_type):
    """
    Get technology-specific security guidance

    Args:
        app_type: Technology/framework (e.g., "Angular", "React", "Vue", etc.)

    Returns:
        String with tech-specific security considerations
    """
    tech_guidance = {
        "Angular": "Angular apps commonly face XSS through template injection, CSP bypass, and insecure API calls. Pay attention to innerHTML usage and HTTP interceptor security.",
        "React": "React applications should watch for XSS via dangerouslySetInnerHTML, insecure dependencies, and state management vulnerabilities. Ensure proper input sanitization.",
        "Vue": "Vue apps need to guard against template injection, v-html XSS, and component communication vulnerabilities. Verify proper escaping in templates.",
        "PHP": "PHP applications are prone to SQL injection, command injection, file upload vulnerabilities, and session hijacking. Use prepared statements and input validation.",
        "Django": "Django apps should ensure CSRF protection is enabled, SQL injection prevention via ORM, and secure template rendering. Check middleware configuration.",
        "Flask": "Flask applications need explicit security measures: enable CSRF protection, use parameterized queries, implement rate limiting, and secure session management.",
        "Express": "Express.js apps require helmet.js for security headers, input validation, SQL injection prevention, and protection against NoSQL injection.",
        "ASP.NET": "ASP.NET applications should use parameterized queries, enable request validation, implement proper authentication, and configure security headers.",
        "Spring": "Spring applications should use Spring Security, prevent SQL injection via JPA/Hibernate, validate inputs, and configure CORS properly.",
        "Laravel": "Laravel apps benefit from built-in CSRF protection, Eloquent ORM for SQL injection prevention, and middleware for authentication. Verify configurations.",
        "WordPress": "WordPress sites need regular updates, plugin security audits, strong authentication, and protection against common CMS vulnerabilities.",
        "Unknown": "General web application security best practices apply. Focus on input validation, output encoding, authentication, and security headers."
    }

    return tech_guidance.get(app_type, tech_guidance["Unknown"])


def calculate_max_score(scan_map):
    """Calculate maximum possible score based on active scans"""
    return sum(OWASP_WEIGHTS.get(category, 10) for category in scan_map.keys())


def analyze_security_headers(headers):
    """Analyze security-related HTTP headers"""
    security_headers = {
        'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
        'X-Frame-Options': headers.get('X-Frame-Options'),
        'Content-Security-Policy': headers.get('Content-Security-Policy'),
        'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
        'X-XSS-Protection': headers.get('X-XSS-Protection'),
    }

    missing_headers = [k for k, v in security_headers.items() if v is None]
    return {
        'present': {k: v for k, v in security_headers.items() if v is not None},
        'missing': missing_headers
    }


def prepare_scan_summary(scan_results):
    """Create a human-readable summary of scan results for the AI"""
    summary = {}

    for scan_code, scan_data in scan_results.items():
        if isinstance(scan_data, dict):
            # Get first result for header analysis
            first_result = scan_data.get('results', [{}])[0] if scan_data.get('results') else {}

            summary[scan_code] = {
                'scan_type': scan_data.get('scan_type', 'unknown'),
                'vulnerabilities_found': scan_data.get('found_vulnerabilities', False),
                'total_fields_tested': scan_data.get('num_fields', 0),
                'successful_exploits': scan_data.get('num_successful', 0),
                'total_attempts': len(scan_data.get('results', [])),
                'target_url': first_result.get('origin_url', 'N/A'),
                'sample_payloads': [
                    r.get('payload') for r in scan_data.get('results', [])[:3]
                ],
                'security_headers': analyze_security_headers(first_result.get('headers', {})) if first_result else None,
                'allows_deeper_traversal': any(
                    r.get('allows_deeper_traversal', False)
                    for r in scan_data.get('results', [])
                )
            }

    return summary


def main(app_type, scan_map, scan_results):
    # Normalize scan codes to OWASP format
    owasp_map, owasp_results = normalize_scan_codes(scan_map, scan_results)

    max_score = calculate_max_score(owasp_map)
    active_weights = {cat: OWASP_WEIGHTS.get(cat, 10) for cat in owasp_map.keys()}

    # Prepare a cleaner summary for the AI
    scan_summary = prepare_scan_summary(owasp_results)

    # Get tech-specific guidance
    tech_guidance = get_tech_specific_guidance(app_type)

    prompt = f"""
    You are an expert web security analyst evaluating scan results from WaspAI, an automated vulnerability scanner.

    **Target Information:**
    - Categories Tested: {json.dumps({k: OWASP_TOP_10[k] for k in owasp_map.keys()}, indent=2)}
    - Scoring System: Maximum {max_score} points (weighted by OWASP severity)
    - Category Weights: {json.dumps(active_weights, indent=2)}

    **Scan Results Summary:**
    {json.dumps(scan_summary, indent=2)}

    **Target Application Information:**
    - Technology Stack: {app_type}
    - Tech-Specific Security Considerations: {tech_guidance}


    **Analysis Instructions:**
    1. **Evaluate each category:**
       - Did the scanner find vulnerabilities?
       evaluate the severity and quantity of vulnerabilities found

    2. **Score each category (0 to max_weight):**
       - **Full points**: No vulnerabilities found AND strong security posture
       - **75-99% points**: Good security with minor improvements needed
       - **50-74% points**: Moderate issues, some vulnerabilities detected
       - **25-49% points**: Significant vulnerabilities found
       - **0-24% points**: Critical vulnerabilities or successful exploits

    3. **Analyze security headers:**
       - Missing critical headers (CSP, HSTS, etc.)
       - Weak configurations
       - Best practice violations

    4. For each category with vulnerabilities, provide:
       - Bullet-pointed remediation recommendations with specific, actionable steps
       - Prioritized by severity (address critical issues first)
       - References to relevant security standards (OWASP) where applicable

    5. **Calculate final score:**
       - Final Score = (Total Points Earned / {max_score}) × 100
       **Calculate grades based on overall_score:**
        - A: 90-100
        - B: 80-89
        - C: 70-79
        - D: 60-69
        - F: 0-59

    **Required JSON Output Format:**
{{
  "overall_score": <number 0-100, calculated as (total_points/max_possible_points)*100>,
  "total_points": <number, sum of all category scores>,
  "max_possible_points": {max_score},
  "grade": "<A|B|C|D|F based on overall_score>",
  "risk_level": "critical|high|medium|low|minimal",
  "technology_stack": "{app_type}",
  "categories": [
    {{
      "category_id": "A03",
      "category_name": "Injection",
      "score": <single number 0-{max_score}, NOT a fraction>,
      "max_score": <category max weight>,
      "vulnerabilities_found": <number of vulnerabilities>,
      "fields_tested": <number>,
      "successful_exploits": <number>,
      "severity": "critical|high|medium|low|none",
      "evidence": ["Brief description of findings"],
      "remediation": [
        {{
          "priority": "critical|high|medium|low",
          "issue": "Specific vulnerability or weakness",
          "recommendation": "Detailed fix with {app_type}-specific code examples",
          "reference": "OWASP A03:2021, CWE-89, etc."
        }}
      ],
      "security_headers_analysis": {{
        "missing_headers": ["ONLY list headers that are ACTUALLY missing from scan results"],
        "recommendations": "What to add for {app_type}"
      }}
    }}
  ],
      ],
      "summary": "2-3 sentence executive summary of security posture",
      "key_findings": [
        "Most important finding 1",
        "Most important finding 2",
        "Most important finding 3"
      ],
      "immediate_actions": [
        "Top priority action 1",
        "Top priority action 2"
      ]
    }}
    
    **CRITICAL OUTPUT REQUIREMENTS:**
    1. Score format MUST be a single number (e.g., "score": 12), NOT a fraction string  
    2. Grade MUST match the overall_score:
   - 90-100 = "A"
   - 80-89 = "B"  
   - 70-79 = "C"
   - 60-69 = "D"
   - 0-59 = "F"
    3. Calculate total_points as the SUM of all category scores
    4. Overall_score = (total_points / max_possible_points) * 100
    5. Only list headers that are ACTUALLY missing from the scan results

    **Important Notes:**
    - Be specific about SQL injection payloads tested
    - Highlight if allows_deeper_traversal is true (indicates auth bypass)
    - Comment on the target's security headers configuration
    - Even if no vulnerabilities found, assess the security posture
    - Provide actionable, {app_type}-specific remediation steps with code examples
    - Provide actionable remediation steps, not generic advice
    """

    try:
        response = client.chat.completions.create(
            model=gpt_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a security analyst. Output ONLY valid JSON. No markdown formatting, no explanations outside JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        message = response.choices[0].message

        # Parse JSON response
        if hasattr(message, "parsed"):
            feedback = message.parsed
        else:
            try:
                # Remove potential markdown formatting
                content = message.content.strip()
                if content.startswith("```json"):
                    content = content.split("```json")[1].split("```")[0].strip()
                elif content.startswith("```"):
                    content = content.split("```")[1].split("```")[0].strip()

                feedback = json.loads(content)
            except json.JSONDecodeError as je:
                print(f"[!] JSON parsing error: {je}")
                print(f"[!] Raw content: {message.content[:500]}")
                feedback = create_error_response(owasp_map, owasp_results, app_type)

        # Validate structure
        if not validate_response(feedback):
            print("[!] Warning: Response missing expected fields")

        return format_report(feedback)

    except Exception as e:
        print(f"[!] OpenAI API error: {e}")
        return create_error_response(owasp_map, owasp_results, app_type)


def create_error_response(scan_map, scan_results, app_type):
    """Create a fallback response if AI fails"""
    return {
        "error": "AI analysis failed, using fallback scoring",
        "overall_score": 0,
        "total_points": 0,
        "max_possible_points": calculate_max_score(scan_map),
        "grade": "F",
        "risk_level": "unknown",
        "technology_stack": app_type,
        "categories": [
            {
                "category_id": cat,
                "category_name": OWASP_TOP_10[cat],
                "score": 0,
                "max_score": OWASP_WEIGHTS.get(cat, 10),
                "vulnerabilities_found": scan_results.get(cat, {}).get('found_vulnerabilities', False),
                "remediation": [
                    {"priority": "high", "issue": "Unable to analyze", "recommendation": "Manual review required",
                     "reference": "N/A"}]
            }
            for cat in scan_map.keys()
        ],
        "summary": "Automated analysis failed. Manual security review recommended."
    }


def validate_response(feedback):
    """Validate the AI response has required fields"""
    required_fields = ["overall_score", "categories", "summary"]
    return all(field in feedback for field in required_fields)


def format_report(feedback):
    """Convert JSON feedback into a readable security report"""
    if "error" in feedback and not feedback.get("categories"):
        return f"❌ Error: {feedback['error']}"

    report = []

    # Header
    report.append("=" * 70)
    report.append("WASPAI SECURITY SCAN REPORT")
    report.append("=" * 70)

    # Technology Stack
    if feedback.get('technology_stack'):
        report.append(f"\n🔧 Technology Stack: {feedback['technology_stack']}")

    # Overall Score
    score = feedback.get('overall_score', 0)
    grade = feedback.get('grade', 'F')
    risk = feedback.get('risk_level', 'unknown').upper()

    report.append(f"🎯 Overall Security Score: {score:.1f}/100 (Grade: {grade})")
    report.append(f"📊 Points Earned: {feedback.get('total_points', 0)}/{feedback.get('max_possible_points', 100)}")
    report.append(f"⚠️  Risk Level: {risk}")

    # Key Findings
    if feedback.get('key_findings'):
        report.append("\n" + "=" * 70)
        report.append("🔍 KEY FINDINGS")
        report.append("=" * 70)
        for i, finding in enumerate(feedback['key_findings'], 1):
            report.append(f"{i}. {finding}")

    # Immediate Actions
    if feedback.get('immediate_actions'):
        report.append("\n" + "=" * 70)
        report.append("🚨 IMMEDIATE ACTIONS REQUIRED")
        report.append("=" * 70)
        for i, action in enumerate(feedback['immediate_actions'], 1):
            report.append(f"{i}. {action}")

    # Executive Summary
    report.append("\n" + "=" * 70)
    report.append("📝 EXECUTIVE SUMMARY")
    report.append("=" * 70)
    report.append(feedback.get('summary', 'No summary available'))

    # Category Breakdown
    report.append("\n" + "=" * 70)
    report.append("DETAILED CATEGORY ANALYSIS")
    report.append("=" * 70)

    for category in feedback.get('categories', []):
        cat_id = category.get('category_id', 'N/A')
        cat_name = category.get('category_name', 'Unknown')
        score = category.get('score', 0)
        max_score = category.get('max_score', 10)
        severity = category.get('severity', 'unknown').upper()
        vuln_found = category.get('vulnerabilities_found', False)

        report.append(f"\n[{cat_id}] {cat_name}")
        report.append(f"Score: {score}/{max_score} | Severity: {severity}")
        report.append(f"Vulnerabilities Found: {'✅ YES' if vuln_found else '❌ NO'}")
        report.append(f"Fields Tested: {category.get('fields_tested', 0)}")
        report.append(f"Successful Exploits: {category.get('successful_exploits', 0)}")

        # Evidence
        if category.get('evidence'):
            report.append("\n  📋 Evidence:")
            for evidence in category['evidence']:
                report.append(f"    • {evidence}")

        # Security Headers
        if category.get('security_headers_analysis'):
            headers = category['security_headers_analysis']
            if headers.get('missing_headers'):
                report.append(f"\n  🔒 Missing Security Headers: {', '.join(headers['missing_headers'])}")
            if headers.get('recommendations'):
                report.append(f"  💡 {headers['recommendations']}")

        # Remediation Steps
        if category.get('remediation'):
            report.append("\n  🔧 REMEDIATION STEPS:")
            for i, rem in enumerate(category['remediation'], 1):
                priority = rem.get('priority', 'unknown').upper()
                issue = rem.get('issue', 'N/A')
                recommendation = rem.get('recommendation', 'N/A')
                reference = rem.get('reference', '')

                report.append(f"\n    {i}. [{priority}] {issue}")
                report.append(f"       → {recommendation}")
                if reference:
                    report.append(f"       📚 Reference: {reference}")

    report.append("\n" + "=" * 70)
    report.append("End of Report")
    report.append("=" * 70)

    return "\n".join(report)