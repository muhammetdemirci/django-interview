import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, recipients):
    sender = "m7demirci60@gmail.com"
    password = "srlo brdn smix wmsg"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")

