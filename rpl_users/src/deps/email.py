import logging
import secrets
import smtplib
import ssl
from email.message import EmailMessage
from typing import Annotated

from fastapi import Depends

from rpl_users.src.config.env import (
    FRONTEND_URL,
    RPL_HELP_EMAIL_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
    RPL_HELP_EMAIL_USER,
)
from rpl_users.src.repositories.models.course import Course
from rpl_users.src.repositories.models.user import User


class EmailHandler:

    def __send_email(self, to_address, subject, body):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = RPL_HELP_EMAIL_USER
        msg["To"] = to_address
        msg.set_content(body)
        msg.add_alternative(body, subtype="html")

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                server.login(RPL_HELP_EMAIL_USER, RPL_HELP_EMAIL_PASSWORD)
                server.send_message(msg)
        except smtplib.SMTPException as e:
            logging.getLogger("uvicorn.error").error(f"Failed to send email to {to_address}. Error: {e}")

    # ==============================================================================

    def send_validation_email(self, to_address) -> str:
        token = secrets.token_urlsafe()
        validation_link = f"{FRONTEND_URL}/user/validateEmail?token={token}"
        subject = "RPL: Validación de e-mail"
        body = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <body>
                    <p>Para validar tu e-mail, hacé click en el siguiente link: <a href="{validation_link}">VALIDAR E-MAIL</a></p>
                    <p>Esperamos que te guste la plataforma!</p>
                </body>
                </html>
        """
        self.__send_email(to_address, subject, body)
        return token

    def send_password_reset_email(self, to_address) -> str:
        token = secrets.token_urlsafe(32)
        reset_link = f"{FRONTEND_URL}/user/changePassword?token={token}"
        subject = "RPL: Reseteo de contraseña"
        body = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <body>
                    <p>Para reestrablecer tu contraseña, hacé click en el siguiente link: <a href="{reset_link}">REESTABLECER
                CONTRASEÑA</a></p>
                    <p>Guardala bien papafrita!</p>
                </body>
                </html>
            """
        self.__send_email(to_address, subject, body)
        return token

    def send_course_acceptance_email(self, to_address: str, user_data: User, course_data: Course):
        link = f"{FRONTEND_URL}/course/{course_data.id}"
        subject = "RPL: Aceptación de curso"
        user_fullname = f"{user_data.name} {user_data.surname}"
        course_name = f"{course_data.subject_id} - {course_data.name}"
        course_description = f"{course_data.description or ''}"
        body = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <body>
                    <p>Bienvenido {user_fullname}, fuiste aceptado en el curso
                    {course_name}
                    </p>
                    </p>
                    <p>{course_description}</p>
                    </p>
                    <p>Para acceder al curso podes hacer click <a href="{link}">acá</a></p>
                </body>
                </html>
            """
        self.__send_email(to_address, subject, body)


# Dependency =============================


def get_email_handler():
    return EmailHandler()


EmailHandlerDependency = Annotated[EmailHandler, Depends(get_email_handler)]


# ==========================================
