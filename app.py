"""
DivorCEmate – Flask Email Backend
Handles contact form submissions and sends emails via Gmail SMTP.

Setup:
  1. Copy .env.example to .env and fill in your credentials
  2. pip install -r requirements.txt
  3. python app.py
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# ─── Load environment variables ──────────────
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from the frontend (any origin)

# ─── SMTP Configuration ───────────────────────
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587
SENDER_EMAIL  = os.environ.get("SENDER_EMAIL")   # Your Gmail address
SENDER_PASS   = os.environ.get("SENDER_PASS")    # Gmail App Password (NOT your login password)
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "divorcematequeries@gmail.com")


# ─── Helper: send email via Gmail SMTP ────────
def send_email(name, email, phone, subject, message):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[DivorCEmate Enquiry] {subject} – {name}"
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECEIVER_EMAIL
    msg["Reply-To"] = email  # Replying goes directly to the enquirer

    # Plain-text fallback
    plain_body = (
        f"New Enquiry from DivorCEmate Website\n"
        f"=====================================\n\n"
        f"Name:    {name}\n"
        f"Email:   {email}\n"
        f"Phone:   {phone}\n"
        f"Subject: {subject}\n\n"
        f"Message:\n{message}\n\n"
        f"---\nSent via DivorCEmate Contact Form"
    )

    # HTML email body
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

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASS)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())


# ─── Routes ───────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "DivorCEmate email server is running ✅"}), 200


@app.route("/send-email", methods=["POST"])
def handle_contact():
    # Validate environment config
    if not SENDER_EMAIL or not SENDER_PASS:
        return jsonify({
            "error": "Server misconfiguration: SENDER_EMAIL or SENDER_PASS not set in .env"
        }), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request – expected JSON body"}), 400

    # Extract and validate fields
    name    = (data.get("name") or "").strip()
    email   = (data.get("email") or "").strip()
    phone   = (data.get("phone") or "Not provided").strip()
    subject = (data.get("subject") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not subject or not message:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        send_email(name, email, phone, subject, message)
        return jsonify({"success": True, "message": "Email sent successfully"}), 200
    except smtplib.SMTPAuthenticationError:
        return jsonify({
            "error": "SMTP authentication failed. Check your Gmail App Password in .env"
        }), 500
    except Exception as exc:
        return jsonify({"error": f"Failed to send email: {str(exc)}"}), 500


# ─── Entry Point ──────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"✅  DivorCEmate email server running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
