# Email Setup for NeoSignal

The daily report is emailed at 9:00 AM IST every day via Gmail SMTP.
You need to add **3 repository secrets** once to activate this.

---

## Step 1 — Create a Gmail App Password

Gmail requires an App Password (not your regular password) for SMTP.

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Select app: **Mail** → Select device: **Other** → type `NeoSignal`
5. Click **Generate** — copy the 16-character password shown

---

## Step 2 — Add Secrets to GitHub

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 3 secrets:

| Secret Name      | Value                                      |
|------------------|--------------------------------------------|
| `EMAIL_USERNAME` | Your Gmail address (e.g. `you@gmail.com`)  |
| `EMAIL_PASSWORD` | The 16-char App Password from Step 1       |
| `EMAIL_TO`       | Recipient email (can be same as username)  |

---

## Step 3 — Test

Go to **Actions** → **NeoSignal Daily Report** → **Run workflow**

You should receive the PDF in your inbox within ~2 minutes.

---

## Troubleshooting

- `Email step failed` but PDF still committed → check secrets spelling (case-sensitive)
- `Less secure app` error → you must use App Password, not your real Gmail password
- Not receiving email → check spam folder; Gmail may hold first automated emails

The workflow uses `continue-on-error: true` on the email step — so even if email
fails, the PDF is always committed to the repo in `reports/`.
