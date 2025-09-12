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

### Goals for the upcoming week
- This weekend - do a lot more with the injections and generating responses
- Get files/folders created so I can be more clear on how things will look
- focus on injections and see if I can get some sort of AI feedback on something 
- LEARN about injections a lot more and see what a response would look like from an injection
