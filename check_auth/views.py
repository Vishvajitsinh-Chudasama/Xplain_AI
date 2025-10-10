from django.shortcuts import render
from django.contrib import messages
from .models import UserInfo, OTP
import json
import random
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
def login_view(request):
    return render(request, 'login.html')

def send_email(to_email, subject, message_html):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "sender@gmail.com"
    SENDER_PASSWORD = "password"

    msg = MIMEMultipart("alternative")
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message_html, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

@csrf_exempt
def signup_view(request):
    if request.method == "GET":
        return render(request, "signup.html")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            action = data.get("action")

            if action == "send":
                email = data.get("email")
                name = data.get("name")

                if UserInfo.objects.filter(email=email).exists():
                    return JsonResponse({"error": "Email already registered!"}, status=400)

                otp_code = str(random.randint(100000, 999999))
                OTP.objects.update_or_create(email=email, defaults={"otp": otp_code})

                BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                template_path = os.path.join(BASE_DIR, "templates", "otp.html")

                try:
                    with open(template_path, "r", encoding="utf-8") as file:
                        html_template = file.read()
                        email_html_content = html_template.replace("{{ username }}", name).replace("{{ otp }}", otp_code)
                except FileNotFoundError:
                    logger.warning("Email template file not found!")
                    email_html_content = f"<h1>Your OTP</h1><p>Hello {name}, your OTP is: {otp_code}</p>"

                if send_email(
                    subject="Your XplainAI OTP Code",
                    message_html=email_html_content,
                    to_email=email
                ):
                    return JsonResponse({"message": "OTP sent successfully!"}, status=200)
                else:
                    return JsonResponse({"error": "Failed to send OTP email."}, status=500)

            elif action == "verify":
                email = data.get("email")
                otp_entered = data.get("otp")

                try:
                    otp_record = OTP.objects.get(email=email)
                except OTP.DoesNotExist:
                    return JsonResponse({"error": "No OTP found. Please request again."}, status=400)

                if otp_record.otp == otp_entered and otp_record.is_valid():
                    UserInfo.objects.create(
                        name=data.get("name"),
                        email=email,
                        phone=data.get("phone"),
                        password=data.get("password")  # Note: Passwords should be hashed in a real application
                    )
                    otp_record.delete()
                    return JsonResponse({"message": "Account created successfully"}, status=201)
                else:
                    return JsonResponse({"error": "Invalid or expired OTP"}, status=400)

            return JsonResponse({"error": "Invalid action"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return JsonResponse({"error": "An internal server error occurred."}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)