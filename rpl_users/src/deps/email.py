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


class EmailHandler:

    def __send_email(to_address, subject, body):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = RPL_HELP_EMAIL_USER
        msg["To"] = to_address
        msg.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(RPL_HELP_EMAIL_USER, RPL_HELP_EMAIL_PASSWORD)
            server.send_message(msg)
            logging.info(f"Email sent to {to_address} with subject: {subject}")

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
        reset_link = f"{FRONTEND_URL}/user/resetPassword?token={token}"
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

    def send_course_acceptance_email(self, to_address, user_data, course_data):
        # TODO: Add type hints
        link = f"{FRONTEND_URL}/course/{course_data.id}"
        subject = "RPL: Aceptación de curso"
        body = f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <body>
                    <p>Bienvenido <span text="{user_data.name}"></span> <span text="{user_data.surname}"></span>, fuiste aceptado en el curso
                    <span text="{course_data.subject_id}"></span> - <span text="{course_data.name}"></span>
                    </p>
                    </p>
                    <p text="{course_data.description}"></p>
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
