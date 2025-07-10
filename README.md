# Helpdesk Ticket Summary Automation

This project automates the process of generating and sending daily summaries of active helpdesk tickets. It connects to a helpdesk system via API, collects relevant data, organizes it by priority, status, and assigned agent, and sends a structured HTML report to designated recipients.

## Features

- Connects to your helpdesk system using API credentials
- Fetches all open tickets (excluding closed/resolved)
- Organizes ticket data by:
  - Status
  - Priority
  - Assigned agent
- Builds a clean HTML summary of the day’s ticket activity
- Sends automated summary emails via SMTP

## Configuration

Update the following values in `daily_summary.py`:

- `HELPDESK_DOMAIN`: your helpdesk system domain (e.g., `yourcompany.helpdesk.com`)
- `API_KEY`: your API key for authentication
- `EMAIL_SENDER`: email address used to send the summary
- `EMAIL_PASSWORD`: SMTP password or app-specific password
- `EMAIL_RECIPIENTS`: list of recipient email addresses
- `SMTP_SERVER` / `SMTP_PORT`: your mail server settings

All sensitive information should be stored securely and not hardcoded for production use.

## Dependencies

- `requests`
- `smtplib` (standard library)
- `email` (standard library)

You can install the required third-party library with:

```bash
pip install requests
```

## Usage

Run the script with:

```bash
python daily_summary.py
```

The script will:

1. Fetch ticket data from your helpdesk
2. Format the data into an HTML summary
3. Send the summary to the configured recipients

## Disclaimer

This script is a generalized version of an automation tool used in a real-world IT environment. All sensitive data and proprietary identifiers have been removed or anonymized.
