# WaspAI
- An AI-integrated web scanner 

## Description
WaspAI is a tool built for Web Developers to test their website while in development or production.It utilizes Selenium 
to automate web interactions and scans for specific fields that can have potential vulnerabilities. OpenAI API calls 
are made to look through the results of these vulnerabilities and give the target website a security rating, which is
on a scale of 0-100, with 100 being a very secure website and 0 being one that's very vulnerable. NOTE there's still
more to be done with this project, as of now only vulnerabilities for injections will properly work. Files are created 
in the "scans" directory, all labeled for one of the OWASP 10 top web vulnerabilities. Code can be written and integrate
easily to work. all have a main function written.

## Dependencies
```
    "python-dotenv>=0.21.0",
    "openai~=1.105.0",
    "requests~=2.32.5",
    "selenium~=4.24.0",
    "webdriver-manager~=4.0.2"
    an OpenAI API Key
```

## Getting Started
To Utilize WaspAI you must first install from my GitHub repository (https://github.com/JoeyDiMart/AI-Web-Scanner). 
After installing, open a terminal window to "~/AI-Web-Scanner/waspai/". When opening, the keyword "waspai" can run the 
program. a .env file needs to be created in "~/AI-Web-Scanner/" with your OpenAI API key in the format "API_KEY={key}".

## Installation Steps
1. Clone the repository:
```bash
   git clone https://github.com/JoeyDiMart/AI-Web-Scanner.git
   cd AI-Web-Scanner/waspai
```

2. Install dependencies:
```bash
   pip install .
```
   Or for development mode:
```bash
   pip install -e .
```

3. Configure an OpenAI API key in the .env file

4. From the `~/AI-Web-Scanner/waspai/` directory, run:
```bash
waspai
```
5. To specify a target and get the scanner to start, run:
```bash
waspai {ip_address/domain_name} 
```
6. To run a specific scan only, add -scan {scan_type}. The help 
function will provide a dictionary of scans and their abbreviations, to only test for injection 
vulnerabilities and server-side request forgeries, run:
```bash
waspai {ip_address/domain_name} -scan i,r
```
7. The scanner will also attempt to identify what framework the website was
created with, and at the very least can identify if it's static or dynamic.
To bypass this feature or if the app type is known you can run:
```bash
waspai {ip_address/domain_name} -t {app_type}
```

7. The scanner will default only go a depth of 1, meaning anything that causes a redirect will be followed once, if you'd 
like to go further and follow more bread crumbs, you can run the following:
```bash
waspai {ip_address/domain_name} -depth {max_depth}
```