import os
from flask import Flask, Response, request
from celery_app import make_celery
from dotenv import load_dotenv
import json


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


load_dotenv()

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='amqp://guest@localhost:5672//'
)


celery = make_celery(app)


@celery.task()
def send_email(receptor, message):
    msg = MIMEMultipart()
    password = os.environ.get('PASS_EMAIL')
    msg['From'] = os.environ.get('USER_EMAIL')
    msg['To'] = message
    msg['Subject'] = 'Test Platzi'

    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


@app.route("/send_mail", methods=["POST"])
def send_mail():
    try:
        receptor = request.values.get('receptor')
        message = request.values.get('message')
        send_email.delay(receptor, message)
        return Response('0K', status=200)
    except Exception as ex:
        error = {'error': ex}
        error = json.dumps(error)
        return Response(response=error, status=200, content_type="application/json")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
