"""
DivorCEmate – Flask Backend
Serves the frontend and sends contact form emails via SendGrid HTTP API.
SendGrid bypasses Render's SMTP port block by using HTTPS (port 443).

Local dev:
  1. Copy .env.example → .env and fill credentials
  2. pip install -r requirements.txt
  3. python app.py
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# ─── Paths ───────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__)
CORS(app)

# ─── Email Configuration ──────────────────────
SENDGRID_API_KEY = (os.environ.get("SENDGRID_API_KEY") or "").strip()
SENDER_EMAIL     = (os.environ.get("SENDER_EMAIL") or "").strip()
RECEIVER_EMAIL   = (os.environ.get("RECEIVER_EMAIL") or "divorcematequeries@gmail.com").strip()


# ─── Helper: send email via SendGrid API ──────
def send_email(name, email, phone, subject, message):
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content, ReplyTo

    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background:#f9f6f0; margin:0; padding:24px;">
      <div style="max-width:560px; margin:auto; background:#fff; border-radius:12px;
                  box-shadow:0 4px 20px rgba(0,0,0,0.08); overflow:hidden;">
        <div style="background: linear-gradient(135deg,#8b5e3c,#c4956a); padding:28px 32px;">
          <h2 style="color:#fff; margin:0; font-size:22px;">New Enquiry – DivorCEmate</h2>
        </div>
        <div style="padding:28px 32px;">
          <table style="width:100%; border-collapse:collapse; font-size:15px;">
            <tr><td style="padding:8px 0; color:#666; width:90px;"><strong>Name</strong></td>
                <td style="padding:8px 0; color:#222;">{name}</td></tr>
            <tr><td style="padding:8px 0; color:#666;"><strong>Email</strong></td>
                <td style="padding:8px 0; color:#222;"><a href="mailto:{email}" style="color:#8b5e3c;">{email}</a></td></tr>
            <tr><td style="padding:8px 0; color:#666;"><strong>Phone</strong></td>
                <td style="padding:8px 0; color:#222;">{phone}</td></tr>
            <tr><td style="padding:8px 0; color:#666;"><strong>Subject</strong></td>
                <td style="padding:8px 0; color:#222;">{subject}</td></tr>
          </table>
          <hr style="border:none; border-top:1px solid #eee; margin:20px 0;">
          <p style="color:#666; font-size:13px; margin:0 0 8px 0;"><strong>Message:</strong></p>
          <p style="color:#333; font-size:15px; line-height:1.6; white-space:pre-wrap;">{message}</p>
        </div>
        <div style="background:#f9f6f0; padding:16px 32px; font-size:12px; color:#999; text-align:center;">
          Sent via DivorCEmate Contact Form
        </div>
      </div>
    </body>
    </html>
    """

    plain_body = (
        f"New Enquiry from DivorCEmate\n"
        f"============================\n\n"
        f"Name:    {name}\n"
        f"Email:   {email}\n"
        f"Phone:   {phone}\n"
        f"Subject: {subject}\n\n"
        f"Message:\n{message}"
    )

    mail = Mail(
        from_email=Email(SENDER_EMAIL, "DivorCEmate"),
        to_emails=To(RECEIVER_EMAIL),
        subject=f"[DivorCEmate Enquiry] {subject} – {name}",
        plain_text_content=plain_body,
        html_content=html_body
    )
    mail.reply_to = ReplyTo(email, name)   # replying goes to the enquirer

    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code


# ─── Static File Routes ───────────────────────
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/style.css")
def serve_css():
    return send_from_directory(BASE_DIR, "style.css")

@app.route("/script.js")
def serve_js():
    return send_from_directory(BASE_DIR, "script.js")

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, "assets"), filename)


# ─── Email API ────────────────────────────────
@app.route("/send-email", methods=["POST"])
def handle_contact():
    if not SENDGRID_API_KEY or not SENDER_EMAIL:
        return jsonify({"error": "Server misconfiguration: SENDGRID_API_KEY or SENDER_EMAIL not set"}), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request – expected JSON body"}), 400

    name    = (data.get("name")    or "").strip()
    email   = (data.get("email")   or "").strip()
    phone   = (data.get("phone")   or "Not provided").strip()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not subject or not message:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        send_email(name, email, phone, subject, message)
        return jsonify({"success": True}), 200
    except Exception as exc:
        return jsonify({"error": f"Failed to send email: {str(exc)}"}), 500


# ─── Entry Point ──────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"✅  DivorCEmate server running → http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
