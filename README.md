# 💬 Simple Contact Lens

A tiny automation tool that reminds you when it's time to reconnect with people in your Nextcloud address book — via email and WhatsApp.

---

## 🚀 What It Does

- Parses your **Nextcloud CardDAV address book**
- Detects contacts with a custom note like `##CI=30` (for a 30-day contact interval)
- Stores relevant contacts (name, email, phone, interval) in a local database
- Sends you a beautiful **HTML email** with all people who are due for contact
- Lets you click to open **WhatsApp chats**
- Updates the reminder cycle automatically

---

## 🛠️ Requirements

- Python 3.7+
- A working [Nextcloud](https://nextcloud.com) CardDAV address book
- SMTP credentials to send emails (e.g. Gmail, Mailbox.org, etc.)

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/simple_contact_lens.git
cd simple_contact_lens
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure your credentials

Copy the config template and fill in your values:

```bash
cp config_template.py config.py
nano config.py
```

Fill in your:
- Nextcloud CardDAV URL (e.g. `https://yourdomain/remote.php/dav/addressbooks/users/USERNAME/contacts`)
- Nextcloud username/password
- SMTP server details (email sender, receiver, host, port, password)

---

## ✏️ How to Use It

### 1. Mark your contacts in Nextcloud

Add `##CI=XX` to the **Notes** field of any contact  
(e.g. `##CI=60` for every 60 days)

### 2. Run manually

```bash
./run.sh
```

### 3. Or schedule via cron

```bash
crontab -e
```

Add this line (adjust path as needed):

```bash
0 8 * * * /absolute/path/to/simple_contact_lens/run.sh
```

---

## 📧 Email Preview

You’ll receive an email like this:

| Name       | Email                  | WhatsApp              |
|------------|------------------------|------------------------|
| Jane Doe   | jane@example.com       | [491701234567](https://wa.me/491701234567) |

Each phone number links to WhatsApp. Each email opens your email client.

---

## 🔐 Privacy

This tool runs locally on your machine or VPS. No data is sent anywhere — except through your own SMTP server to email yourself reminders.

---

## 🤝 Contributions

Pull requests welcome — especially for:

- alternate contact sources (Google, iCloud, CSV)
- additional messaging platforms (Signal, Telegram)
- optional web dashboard or notification UI

---

## 📄 License

MIT — use freely, modify boldly, share generously.
