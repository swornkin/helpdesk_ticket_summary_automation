import requests
import smtplib
from datetime import datetime
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === CONFIGURATION ===
HELPDESK_DOMAIN = "yourcompany.helpdesk.com"  # Generic domain name
API_KEY = "your_api_key_here"
EMAIL_SENDER = "your_email@example.com"
EMAIL_PASSWORD = "your_email_password_here"
EMAIL_RECIPIENTS = [
    "recipient1@example.com",
    "recipient2@example.com",
    "recipient3@example.com"
]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

headers = {
    "Content-Type": "application/json"
}
auth = (API_KEY, "X")

# === GET STATUS NAME MAP ===
def get_status_name_map():
    url = f"https://{HELPDESK_DOMAIN}/api/v2/ticket_fields"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    fields = response.json()

    for field in fields:
        if field["type"] == "default_status" or field["label"] == "Status":
            return {int(k): v for k, v in field["choices"].items()}
    return {}

# === GET OPEN TICKETS (ALL STATUSES EXCEPT CLOSED/RESOLVED) ===
def get_open_tickets(statuses):
    excluded_labels = {"Closed", "Resolved"}
    valid_status_ids = {
        sid for sid, label in statuses.items()
        if isinstance(label, list) and label[0].strip() not in excluded_labels
    }

    all_tickets = []
    page = 1
    while True:
        url = (
            f"https://{HELPDESK_DOMAIN}/api/v2/tickets?"
            f"updated_since=1970-01-01T00:00:00Z&per_page=100&page={page}"
        )
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        page_tickets = response.json()

        for t in page_tickets:
            if t["status"] in valid_status_ids:
                all_tickets.append(t)

        if len(page_tickets) < 100:
            break
        page += 1

    print(f"Total active tickets: {len(all_tickets)}")
    return all_tickets

# === GET AGENT NAMES ===
def get_agent_name_map():
    url = f"https://{HELPDESK_DOMAIN}/api/v2/agents"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    data = response.json()

    agent_map = {}
    for agent in data:
        agent_id = agent["id"]
        name = agent["contact"]["name"]
        agent_map[agent_id] = name
    return agent_map

# === BUILD HTML EMAIL SUMMARY ===
def build_email_summary(tickets, agent_names, statuses):
    priorities = {1: "Low", 2: "Medium", 3: "High", 4: "Urgent"}
    prio_count = defaultdict(int)
    status_count = defaultdict(int)
    agent_status_counts = defaultdict(lambda: defaultdict(int))

    for t in tickets:
        prio = t.get("priority", 2)
        status = t.get("status", 2)
        assignee = t.get("responder_id") or "Unassigned"

        prio_count[prio] += 1
        status_count[status] += 1
        agent_status_counts[assignee][status] += 1

    summary = f"<b>Helpdesk Summary – {datetime.now().strftime('%Y-%m-%d')}</b><br><br>"

    summary += "<b>Ticket Priorities:</b><br>"
    for p in sorted(prio_count, reverse=True):
        summary += f"{priorities.get(p, 'Unknown')}: {prio_count[p]}<br>"

    summary += "<br><b>Ticket Statuses:</b><br>"
    for s in sorted(status_count):
        label = statuses.get(s, f"Status {s}")
        if isinstance(label, list):
            label = label[0].strip()
        summary += f"{label}: {status_count[s]}<br>"

    summary += "<br><b>Tickets per Agent:</b><br>"
    for aid, status_counts in agent_status_counts.items():
        name = agent_names.get(aid, "Unassigned") if aid != "Unassigned" else "Unassigned"
        summary += f"<br><u>{name}:</u><br>"
        for status_id, count in status_counts.items():
            label = statuses.get(status_id, f"Status {status_id}")
            if isinstance(label, list):
                label = label[0].strip()
            summary += f"- {label}: {count}<br>"

    return summary

# === SEND EMAIL ===
def send_email(summary_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Daily Helpdesk Ticket Summary"
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECIPIENTS)

    body = MIMEText(summary_html, "html")
    msg.attach(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENTS, msg.as_string())

# === MAIN ===
if __name__ == "__main__":
    statuses = get_status_name_map()
    tickets = get_open_tickets(statuses)
    agent_names = get_agent_name_map()
    summary = build_email_summary(tickets, agent_names, statuses)
    send_email(summary)