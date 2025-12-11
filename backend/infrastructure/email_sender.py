from email.message import EmailMessage
import smtplib
from typing import final

from result import Err, Ok, Result

from backend.config import CONFIG
from backend.domain.user import EmailAddress, ValidationToken


@final
class BrevoEmailSender:
    __slots__ = ()

    def send_validation_email(
        self, email: EmailAddress, token: ValidationToken
    ) -> Result[None, str]:
        message = EmailMessage()
        message["Subject"] = "Account validation"
        message["From"] = CONFIG.smtp_sender_name
        message["To"] = email.value

        validation_url = f"{CONFIG.deployment_url}/validate?token={token.value}"

        plain_text = f"""Please click the following link to validate your account:

{validation_url}

If the link doesn't work, copy and paste it into your browser.

This link will expire after some time for security reasons."""

        html_content = f"""
        <html>
        <body>
            <h2>Account Validation</h2>
            <p>Please click the button below to validate your account:</p>
            <p>
                <a href=\"{validation_url}\" 
                   style=\"background-color: #4CAF50; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px; display: inline-block;\">\n                   Validate Account
                </a>
            </p>
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p><a href=\"{validation_url}\">{validation_url}</a></p>
            <p><small>This link will expire after some time for security reasons.</small></p>
        </body>
        </html>
        """

        message.set_content(plain_text)
        message.add_alternative(html_content, subtype="html")

        try:
            with smtplib.SMTP(CONFIG.smtp_host, CONFIG.smtp_port) as server:
                server.starttls()
                if CONFIG.smtp_username and CONFIG.smtp_password:
                    server.login(CONFIG.smtp_username, CONFIG.smtp_password)
                server.send_message(message)
            return Ok(None)
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))
