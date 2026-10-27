# Assignment Submission Portal

Flask app where students submit name, registration number, assignment title and a URL.

## Run the application
    py -m pip install -r requirements.txt
    py app.py
Open http://127.0.0.1:5000

## Run the tests
    py -m pytest -v

## Start the local report receiver
    $env:RECEIVER_TOKEN="your-secret"
    py receiver.py
    ngrok http --url=<your-static-domain> 5001
Add repo secrets `RECEIVER_URL` (https://<your-static-domain>/report) and `RECEIVER_TOKEN`.
After every push, GitHub Actions runs the tests and POSTs the report;
the receiver saves it as `test-report.json`.