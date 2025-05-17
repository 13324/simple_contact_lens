# fetch_contacts.py

import requests
import vobject
import sqlite3
import re
from config import NEXTCLOUD_CARDDAV_URL, NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD
from datetime import datetime

def init_db():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            uid TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            interval_days INTEGER,
            last_contacted TEXT
        )
    ''')
    conn.commit()
    return conn

def fetch_addressbook_vcf():
    export_url = NEXTCLOUD_CARDDAV_URL.rstrip('/') + '?export'
    res = requests.get(export_url, auth=(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD))
    if res.status_code == 200:
        return res.text
    else:
        return None

def extract_vcards(multivcard_data):
    cards = []
    for block in multivcard_data.split("BEGIN:VCARD")[1:]:
        vcard_str = "BEGIN:VCARD" + block
        try:
            card = vobject.readOne(vcard_str)
            cards.append(card)
        except:
            continue
    return cards

def parse_interval_from_note(note):
    match = re.search(r'##CI=(\d+)', note)
    if match:
        return int(match.group(1))
    return None

def main():
    vcf_data = fetch_addressbook_vcf()
    if not vcf_data:
        return

    vcards = extract_vcards(vcf_data)
    conn = init_db()
    c = conn.cursor()

    for card in vcards:
        uid = getattr(card, 'uid', None)
        if not uid:
            continue
        uid = uid.value

        full_name = getattr(card, 'fn', None)
        name = full_name.value if full_name else 'Unknown'

        email = getattr(card, 'email', None)
        email_val = email.value if email else None

        phone = getattr(card, 'tel', None)
        phone_val = phone.value if phone else None

        note = getattr(card, 'note', None)
        note_text = note.value if note else ''

        interval = parse_interval_from_note(note_text)

        if interval is not None:
            c.execute('''
                INSERT INTO contacts (uid, name, email, phone, interval_days, last_contacted)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(uid) DO UPDATE SET
                    name=excluded.name,
                    email=excluded.email,
                    phone=excluded.phone,
                    interval_days=excluded.interval_days
            ''', (uid, name, email_val, phone_val, interval, None))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
