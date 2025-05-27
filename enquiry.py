from flask import Blueprint, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

enquiry_bp = Blueprint('enquiry', __name__)

# Load email credentials from environment variables or config
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "shubhamgautam410322@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "zmdl iocc fwiu mqlx")
EMAIL_RECEIVER = "shubhamgautam410322@gmail.com"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587



@enquiry_bp.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    area = request.form.get('Area')
    property_selected = request.form.get('Property_selected')
    sharing_type = request.form.get('type')
    mobile_number = request.form.get('mobileNumber')
    budget = request.form.get('rent')
    joining_date = request.form.get('joiningDate')

    # Construct the email message
    subject = f"New Enquiry Raised by {name}"
    body = f"""
    Name: {name}
    Location: {area}
    Property: {property_selected}
    Type: {sharing_type}
    Mobile: {mobile_number}
    Budget: {budget}
    Joining Date: {joining_date}
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()

        return jsonify({"message": "Enquiry submitted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
