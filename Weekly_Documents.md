# Week 1 (8.24.25 - 8.29.25)
## **Summary / Beginning notes**
- GitHub repository was created and shared with Dr. Matt
- Created this document to track weekly updates for the independent study.  
- Weeks will run **Saturday → Friday** to align with weekly meetings (held Fridays).
### Technical updates
- No code written yet, just planning out a roadmap of what this project will look like

### Goals for the upcoming week
- Get a document similar to a ReadMe file that explains the projects goal and how to navigate it
- create the files/directories I might need
- determine what GPT model to use (most likely an OpenAI model)
- have a solid idea of the tools I'll be using 
- would be nice to get a simple "Hello World" test of the API 



# Week 2 (8.29.25 - 9.5.25)
## **Summary / Beginning notes**
- This week I did research on the different GPT models that OpenAI has to offer. Models like gpt-4o are Omni models, 
are known as "swiss army knives" and do not have internal reasoning. O-series reasoning models (like o3-mini) have 
internal reasoning and think step by step, which I found to be better for security analysis and feedback
- I decided to use the o3-mini model since the mini model is faster with responses and cheaper, then I can go to o4-mini
as development is completed
- I put $15 into my OpenAI account and got my API key
- I'll need to both Omni and O-series models to see what would be best (mostly will come down with speed and reasoning),
but it's possible to use two models and have them do different tasks
- I ran the hello world program 3 times and got a 3 sentence response (under 1 penny spent)

### Technical updates
- generated API key
- created a Playground folder within main project
- created a working "hello world" program to do an API call

### Goals for the upcoming week
- Research on ways to make this project a CLI
- Figure out the project structure (possible each scan having its own python file) etc.
- Implement one scan at least and print out the results 
- look for a website that I can test (see what is secure vs not secure)



# Week 3 (9.6.25 - 9.12.25)
## **Summary / Beginning notes**
- This week I did a testInjection.py to try out Injections (which was #3 on the list)
- File structure: Since this is a bigger project how I organize this is going to be very important. I want to make it a CLI, 
I think "wasp" is a cool name (since it uses owasp). The plan is to use the command line and do "wasp {url}" then if I want 
to do a specific scan, like an injection, add for example "-i" or something. This is going to have a main project folder,
a core folder that all 10 checks will be using, like one to generate a http request, one to store/record output, send output
to the API and get a response, and a cli.py to convert the command line to the python code. The plan is to use threading
for all 10 scans to be used. __init__.py was suggested by chatGPT to clean up imports 
- I found httpbin.org to send requests and test scans with (it has no vulnerabilities) making it a good control group
- I found a docker image for dvwa (Damn Vulnerable Web Application) on docker hub which is made to be an insecure website to practice 
with. (username: admin password: password) 
** Notes ** 
- using the 'requests' library since it's very popular to make HTTP requests, send data, see responses, etc.
- Injection: trick an input into being a part of the programs instructions (such as a SQL injection trying to make a 
database query)
- URL STRUCTURE: Protocol://Domain/path/path?QueryString#Fragment
- Query string example: example.com/login?user=joey&password=qwerty
- Fragment example: example.com#History (same page just scrolls you to the history section of the page)
- HTTP requests;
GET: retrieve data from a server (fetch a users profile)
POST: send data to the server (create a new user / send login credentials for a user)
PUT: update/replace existing resources (change a password and profile picture)
PATCH: update only certain fields of a resource (specifically change just a password)
DELETE: remove a resource (delete a user)
- Other methods include HEAD, OPTIONS, TRACE, CONNECT
- Status codes: 100 (continue), 101 (switching protocols), 
- 200 (OK), 201 (created), (202) accepted, 204 (no content)
- 3xx codes re redirects
- 4xx are client errors
- 5xx are server errors (look these up later)

### Technical updates
- created two test programs, one for injections, one for simply generating HTTP requests
- set up the docker image for dvwa
- went to https://juice-shop.herokuapp.com/

### Goals for the upcoming week
- This weekend - do a lot more with the injections and generating responses
- Get files/folders created, so I can be more clear on how things will look
- focus on injections and see if I can get some sort of AI feedback on something 
- LEARN about injections a lot more and see what a response would look like from an injection



# Week 4 (9.13.25 - 9.19.25)
## **Summary / Beginning notes**
- The first SQL Injection that worked. Went to 'http://localhost:505/vulnerabilities/sqli/' (the dvwa) and saw a field 
asking for User ID. In the input box I did "' OR '1'='1" which returned the entire database of users (this is an always
true injection which would give all the rows in the db)
- if you put in "'" or "'1" as the input for the id, the website crashes with a 500 error  (an error-based injection)
- "1' UNION SELECT null, version() --" is a union-based injection which allowed me to learn what type of database
version so I have more info on this
- "1' AND SLEEP(5) -- " is a time-based injection, in this example it should take 5 seconds to respond
- I have a second web app that I can use to test injections (and other types of vulnerabilities later), which is the owasp
juice shop
- both the dvwa (port 5050) and juice shop (port 3030) are both run locally on my desktop form a docker image
- dvwa i was unable to log into, I got a token and a session cookie but logging in with python code does not work as i want
- juice shop does let me log in and i even used an injection to log in
- files and directories are made

### Technical updates
- uses the requests and BeautifulSoup python libraries to parse through HTML and send HTTP requests to a web server
- used these modules to find input fields and scan through a web app (first to log in)

### Goals for the upcoming week
- get past a log in screen and to look through all input fields and test out injections
- find what responses from the server I should record and put in txt file
- do a basic injection with juice shop and get a response about it with the openAI 



# Week 5 (9.20.25 - 9.26.25)
## **Summary / Beginning notes**
- I'm going to be using a framework called "Selenium," a link to a guide is here: https://www.geeksforgeeks.org/python/selenium-python-tutorial/
- Selenium will let me automatically search for all types of fields for dynamic and static web pages so it can work for PHP, HTML, and React, etc...
- Got a successful rating and API call so the OpanAI model I'm using can rate the website (gave juiceshop a 0 obviously)
- Using requests and BeautifulSoup made me hit a roadblock for dynamically changing web pages, it COULD/WOULD work 
but the process is a lot harder and would probably not work as well searching for the fields 
- NOTE: selenium interacts with the webpage, it's unlike requests that sends http packets 
- selenium would be perfect for al

### Technical updates
- ai_analysis.py created to make an API call, reading input from a results.txt and printing out the results
- added a injections dictionary to show the different types of injections (SQL, noSQL, command, etc.) and try them for 
multiple fields
- made a list of injectable fields, since juiceshop is not a static HTML web page this is always empty when trying to find all input fields
- added a function so when some sort of result is found it writes to a txt file 

### Goals for the upcoming week
- Empty lists for all types of fields using selenium, like anchors, inputs, buttons, forms
- list of all injection types
- if a response for trying an injection on an input field is 200 or 302, write it to the txt file 
- add an argument if the web app language is known (ex. it ends in .php so it's a static web page)

### AI Generated response for the OWASP top 10 scans using selenium:
1) Broken Access Control — Selenium: very useful

Why Selenium helps

You can emulate different users (login as user A, click UI elements) and check whether UI/flows expose admin-only functionality.
What to test with Selenium

Login as a normal user → try visiting admin URLs, click UI elements that should be hidden.

Manipulate forms/hidden fields in the browser (change role= user → admin) and submit.

Verify UI elements and API responses change when switching accounts.
Example (idea): use Selenium to log in as user, try driver.get("/#/admin") and assert redirect/403.

Use other tools when

You want direct API-level checks (crafting JWTs, tampering tokens) — use requests or a proxy.

2) Cryptographic Failures (Sensitive Data Exposure) — Selenium: limited

When Selenium helps

Check for obvious client-side crypto misuse (e.g., secrets present in page source, encryption done in JS insecurely).

Inspect how data is transmitted in browser (HTTP vs HTTPS) using browser devtools or proxy.
Better tools

Use requests to inspect TLS, Burp/mitmproxy to inspect transport, static analysis / SCA (dependency) scanners and server config checks for cipher suites.

3) Insecure Design / Business Logic Flaws — Selenium: very useful

Why Selenium helps

Business logic issues are often visible only via multi-step UI flows.
What to test with Selenium

Skip workflow steps (e.g., go to checkout success page without paying), replay actions out of order, or attempt race conditions in the UI.

Automate multiple browser instances to test concurrency/race conditions.
Example: automate add-to-cart → tamper with order total in UI → simulate checkout.

4) Security Misconfiguration — Selenium: sometimes useful

When Selenium helps

Detect client-visible misconfigurations (e.g., directory listing rendered, debug info visible, unprotected admin UI).
What to test with Selenium

Visit known admin pages, test default credentials via UI, check error pages for stack traces.
Better tools

Server config scanners, nmap, nikto, and manual review for server headers.

5) Vulnerable & Outdated Components — Selenium: not the primary tool

Why Selenium is limited

Component versions are server-side details; Selenium can’t directly list packages.
What Selenium can do

Observe client-side libs loaded (script tags) and versions; then check if those versions are vulnerable.
Better tools

SCA tools, dependency scanners, npm audit, retire.js, or server-side inventory tools.

6) Identification & Authentication Failures (Broken Authentication) — Selenium: very useful

Why Selenium helps

You can test the full auth flow as a real user: password reset, lockout, MFA, session expiry.
What to test with Selenium

Automate login attempts for brute-force protections, test password reset tokens (click link from email dev interface), test session fixation by setting cookies then logging in.

Confirm logout clears session; test "remember me" behavior.
Combine with requests for token-level manipulation.

7) Software & Data Integrity Failures (e.g., unsafe deserialization, CI tampering) — Selenium: limited

When Selenium helps

If there's a front-end update mechanism (JS loaded remotely) you can observe unexpected script loads or tampered scripts.
Better tools

Build-chain auditing, integrity/hash checks, server-side code review, SCA.

8) Security Logging & Monitoring Failures — Selenium: sometimes useful

Why Selenium has a role

You can generate actions via Selenium and verify whether the UI or admin interface shows logs, or to see if certain error conditions produce visible alerts.
Better tools

Check server-side logs directly, SIEM, or use the logging endpoint / API.

9) Server-Side Request Forgery (SSRF) & Server-side Vulnerabilities — Selenium: limited / indirect

When Selenium helps

If SSRF is triggered from a UI (an upload that causes server to fetch a URL), you can use Selenium to fill the UI and trigger the server action.
What to test with Selenium

Fill the form that triggers server fetch (like URL preview) and supply attacker-controlled callback URLs (point to your local server or Burp Collaborator).
Better tools


Interact with API via requests or use external listeners (Burp Collaborator, OOB tooling) to detect SSRF.



# Week 6 (9.27.25 - 10.2.25)
## **Summary / Beginning notes**
- Finished making files (other than some scans)
- made a pyproject.toml so this can be a custom CLI tool 
- included version history, imports needed, licencing, dependencies, README

### Technical updates
- pyproject.toml made
- main.py finished to take in command line arguments (complete)
- made dictionaries for Scan types and Scan flags
- List for possible app types
- Error handling for bad arguments using the command line tool
- create Scanner object
- add hints for return types

### Goals for the upcoming week
- Finish GetInfo.py 
- self.input_fields = None, self.headers = None, self.cookies = None
- ^ make these full lists/dicts so they can be used for the scans
- Nice to get done: API call to filter data, make the input_fields dict be cleaned up 


# Week 7 (10.3.25 - 10.10.25)
## **Summary / Beginning notes**
- https://www.youtube.com/watch?v=NB8OceGZGjA <- watched this selenium video to show how the scanner can go through web page 
- created the GetInfo.py main method to 
- initialized the Google web driver in main.py
- slow week, input fields and cookies don't fill, need to restructure how headers work

### Technical updates
- added selenium version to the pyproject.toml
- start Google selenium drivers in main.py 
- fixed try/catch blocks in main to work for arg parser and driver
- created main in GetInfo.py
- temp creation of FillFields in GetInfo.py
- installed seleniumwire to capture HTTP requests/responses (so we can get headers only using selenium)

### Goals for the upcoming week
- SPRINT WEEK 
- finish GetInfo
- optimize dictionary of input fields with AI
- https://xkcd.com/



# Week 8 (10.11.25 - 10.20.25)
## **Summary / Beginning notes**
- Started off with Selenium only, decided to use Requests + BeautifulSoup since it's more lightweight and could be a little faster
- will use Selenium for a JS-heavy program, and in general if I can get more fields
- Read the official documentation for Requests and BeautifulSoup, so I know what to expect 
- https://www.w3schools.com/python/module_requests.asp
- restructured main.py a bit

### Technical updates
- tested on https://realpython.github.io/fake-jobs/ since this was given from the beautiful soup documentation 
- added a NEEDS_SELENIUM dict based on the app_type (which gets found if set to auto) -> returns a true/false
- added an optimize_info.py file to categorize the information fields

### Goals for the upcoming week
- finish optimize_info.py and see if the return value has everything I want and is consistent
- fix selenium somehow 
- start scan_manager.py ; this would go through the entry fields available and if it's a field for injections, start injection
on that field



# Week 9 (10.21.25 - 10.24.25)
## **Summary / Beginning notes**
- https://www.geeksforgeeks.org/python/selenium-python-tutorial/
- game plan is to rely on Selenium for all parsing on the website so there's no swapping from bs4 and selenium
- Optimize_fields will 1 take in data about all fields that were found and 2 data from getApp_type function that can 
hint on what type of web app it is. Then I'm hoping the OpenAI API will return the fields data how I want it to be
returned and let me know what type of web app it is. 
- fixes URL args to add http if not included
- adaptive timeout variable for dynamic vs static webpages to change wait time
- stepped through entire code to check for efficiency

### Technical updates
- 

### Goals for the upcoming week
- optimize fields will create a scans list, but if the user input had "-scan i" it should only keep fields that injections can utilize




