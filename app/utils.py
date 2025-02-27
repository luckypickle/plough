import logging
from datetime import datetime, timedelta
from pathlib import Path
from random import random,sample
from typing import Any, Dict, Optional

import emails
from emails.template import JinjaTemplate
from jose import jwt

from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
import uuid
settings: AppSettings = get_app_settings()

Numbers = "1234567890"
Alphabets = "abcdefghijklmnopqrstufwxyz"


def send_email(
        email_to: str,
        subject_template: str = "",
        html_template: str = "",
        environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    project_name = settings.title
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
        template_str = f.read()
    server_host = settings.SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.title,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, str(settings.secret_key), algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, str(settings.secret_key), algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


def send_verify_code(phone: str, verify_code: str):
    import json
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.sms.v20210111 import sms_client, models
    try:
        cred = credential.Credential(settings.SMS_SECRET_ID, settings.SMS_SECRET_KEY)
        client = sms_client.SmsClient(cred, "ap-nanjing")
        req = models.SendSmsRequest()
        params = {
            "PhoneNumberSet": [phone],
            "SignName": settings.SMS_SIGNATURE,
            "SmsSdkAppId": settings.SMS_APP_ID,
            "TemplateId": settings.SMS_TEMPLATE_ID,
            "TemplateParamSet": [verify_code]
        }
        req.from_json_string(json.dumps(params))

        resp = client.SendSms(req)

        return resp.to_json_string()

    except TencentCloudSDKException as err:
        print(err)
def send_verify_email(email:str,verify_code:str):
    import json
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.ses.v20201002 import ses_client, models
    try:
        cred = credential.Credential(settings.SMS_SECRET_ID, settings.SMS_SECRET_KEY)
        client = ses_client.SesClient(cred, "ap-hongkong")
        req = models.SendEmailRequest()
        templateData = json.dumps({"yzm":verify_code})
        params ={
            "FromEmailAddress": settings.SES_FROM_ADDR,
            "Destination": [email],
            "Subject":"Verify code",
            "Template": {
                "TemplateID": settings.SES_TEMPLATE_ID,
                "TemplateData": templateData
            },
        }
        req.from_json_string(json.dumps(params))

        resp = client.SendEmail(req)
        return resp.to_json_string()
    except TencentCloudSDKException as err:
        print(err)

def generate_invite_code():
    return str(uuid.uuid4())[:8]

def random_password_number(length: int):
    return ''.join(sample(Numbers, length))


def random_password_number_lower_letters(length: int):
    return ''.join(sample(Numbers + Alphabets, length))


def random_password_number_upper_letters(length: int):
    return ''.join(sample(Numbers + Alphabets.upper(), length))


def random_password_number_letters(length: int):
    return ''.join(sample(Numbers + Alphabets + Alphabets.upper(), length))


