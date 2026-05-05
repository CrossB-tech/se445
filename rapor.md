Recruitment Pipeline Tracker
This project is a system that uses an automated workflow to automa9cally process uploaded
PDF resume (CVs), score candidates using Gemini AI and export the results to Google Sheets and
send no9fica9ons via Slack.
Main Files
app.py: It is the main executable file of the system. It hosts the Flask-based web server which
processes GET and POST requests and manages the interface. It routes CVs to the background
cv_processor services through the Flask server.
cv_processor.py: It is the core of the system (Processing/Logic Node) covering all data
processing stages from parsing mechanics to saving data to Google Sheets and sending
no9fica9ons through the Slack API. The system evaluates the seniority of the candidates (junior,
senior). Searching to the specific role and evaluate the score and classify the candidate in 3
categories. If the candidate is related to the job defini9on, candidate classified as “interview”. If
the candidate has some missing requirements, the candidate classified as “screen”. If the
candidate is not related to the job defini9on, the candidate classified as “rejected”. If the
candidate has no basic informa9ons like e-mail, phone number, the candidate classified as
“invalid”.
templates/index.html: It is the frontend of the system (Frontend UI Node), a template with a
modern CSS-based sleek and aesthe9c interface using Bootstrap that displays data from Gemini
to the user with dynamic Scoring and Summaries.
.env and creden9als.json: These are system iden9fica9on and configura9on files (Config Nodes),
where the system stores its iden9fica9on and configura9on data. In .env, the system stores its
API keys (Gemini API, Sheet ID, and Slack URL), while creden9als.json contains authoriza9on
data for the Google Sheets API.
requirements.txt: It contains a list of packages and their versions that are installed to ensure the
correct installa9on of the system.
Endpoints & APIs
1. Internal Web Endpoint
Endpoint: / (Root Directory Router)
Methods: GET, POST
Tasks:
GET:
- Renders the web page (upload form)
- Sends the rendered HTML of the web interface as a response to the client
POST:
- Copies the PDF forma`ed (.pdf) CV file uploaded from the interface securely
- Sends the CV to the process_cv() func9on in the backend
2. External Integra9on Nodes
Google Genera9ve AI (Gemini 2.5 Flash):
Usage Context: analyze_cv_with_gemini()
Purpose: To create a smart analysis result in JSON format based on the raw text extracted,
classify it (Hire, Interview, Trial), and calculate the success/fit score out of 100.
Google Sheets API:
Usage Context: append_to_gsheet()
Purpose: To add/archive the candidate's details such as Name, Phone, Score, Summary, Skills,
etc. as a new candidate in the Google Spreadsheet.
Slack Webhook URL:
Usage Context: send_slack_no9fica9on()
Purpose: To no9fy the team by Slack using an automated no9fica9on message only for highprofile/highly suitable candidates who have been rated 'Hire' and added to the system.
Workflow Nodes & Steps
The workflow nodes for the data processing steps carried out by the system will be as follows:
Trigger: The workflow begins with the user uploading the PDF file to the server via the webpage.
Node 1 (PDF Parsing): The Python library, PyPDF2, takes over the task of extrac9ng all the text
on the page, crea9ng a text block (String) (extract_text_from_pdf).
Node 2 (Gemini AI Processing): The extracted text chunks are sent to the Gemini 2.5 Flash API
for processing. The corresponding prompt will create a pure JSON output containing the
classifica9on, score, and summary.
Node 3 (Google Sheets Log): The parsed, clean JSON object will be wri`en into the database
(Google Sheets) columns as a permanent log.
Node 4 (Slack No9fica9on Decision): The Python logic will filter the decisions labeled 'hire'; if the
criteria are sa9sfied, the request will be sent to the Slack webhook.
Return (Cleanup and Visualiza9on): The system safely removes the PDF file from the upload
folder and displays all the successful results on the web interface with the "Gemini Score"
design.
Outputs: The final outputs of the process are:
Permanent Google Sheets rows with candidate data and Scores.

Instant Slack Channel No9fica9ons for the right candidates.
Candidate Score and Summary Card displayed on the screen in real-9me (UI).