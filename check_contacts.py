# check_contacts.py

import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from config import NTFY_URL, EMAIL_SENDER, EMAIL_RECEIVER, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
import requests

def get_due_contacts():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    today = datetime.today().date()
    c.execute('SELECT uid, name, email, phone, interval_days, last_contacted FROM contacts')
    rows = c.fetchall()
    due = []
    for row in rows:
        uid, name, email, phone, interval, last_contacted = row
        if last_contacted:
            last_date = datetime.strptime(last_contacted, "%Y-%m-%d").date()
        else:
            last_date = None

        if not last_date or (today - last_date).days >= interval:
            due.append((uid, name, email, phone))
    return due

def format_whatsapp_link(phone):
    if not phone:
        return ''
    digits = ''.join(filter(str.isdigit, phone))
    if digits.startswith('00'):
        digits = digits[2:]
    elif digits.startswith('0'):
        digits = '49' + digits[1:]  # German number assumption
    return f'https://wa.me/{digits}'

def send_email(due_contacts):
    if not due_contacts:
        return

    html_body = """\
<html>
<head>
  <style>
    table {
      border-collapse: collapse;
      width: 100%;
      font-family: Arial, sans-serif;
    }
    th, td {
      text-align: left;
      padding: 12px;
      border-bottom: 1px solid #ddd;
    }
    th {
      background-color: #2e86de;
      color: white;
    }
    tr:hover {background-color: #f2f2f2;}
    a {
      color: #2e86de;
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }
    h2 {
      font-family: Arial, sans-serif;
      color: #2e86de;
    }
  </style>
</head>
<body>
  <h2>💬 Contact Reminder</h2>
  <p>The following people are due for a check-in:</p>
  <table>
    <tr>
      <th>Name</th>
      <th>Email</th>
      <th>WhatsApp</th>
    </tr>
"""

    text_body = "The following contacts are due for check-in:\n\n"

    for _, name, email, phone in due_contacts:
        wa_link = format_whatsapp_link(phone)
        html_body += f"""\
    <tr>
      <td>{name}</td>
      <td><a href="mailto:{email}">{email}</a></td>
      <td><a href="{wa_link}">{phone}</a></td>
    </tr>
"""
        text_body += f"{name}\nEmail: {email}\nPhone (WA): {wa_link}\n\n"

    html_body += "</table></body></html>"

    msg = MIMEMultipart("alternative")
    msg['Subject'] = '💬 Reach Out to Your Contacts '
    msg['From'] = formataddr(("📇 Contact Reminder 📇", EMAIL_SENDER))
    msg['To'] = EMAIL_RECEIVER

    part1 = MIMEText(text_body, "plain")
    part2 = MIMEText(html_body, "html")

    msg.attach(part1)
    msg.attach(part2)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

def update_last_contacted(uids):
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    today = datetime.today().strftime("%Y-%m-%d")
    for uid in uids:
        c.execute('UPDATE contacts SET last_contacted = ? WHERE uid = ?', (today, uid))
    conn.commit()
    conn.close()

def send_ntfy_notification(due_contacts):
    if not due_contacts:
        return
    names = ", ".join(name for _, name, *_ in due_contacts)
    message = f"You should contact: {names}"
    topic = NTFY_TOPIC if 'NTFY_TOPIC' in globals() else "contact-reminder"
    try:
        requests.post(NTFY_URL, data=message.encode("utf-8"))
    except Exception as e:
        print("Failed to send ntfy notification:", e)

def main():
    due_contacts = get_due_contacts()
    send_email(due_contacts)
    send_ntfy_notification(due_contacts)
    update_last_contacted([uid for uid, *_ in due_contacts])

if __name__ == "__main__":
    main()
