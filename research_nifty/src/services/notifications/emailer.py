from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from config import get_settings


class EmailClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def send(self, subject: str, body: str, to_email: str | None = None) -> bool:
        to_email = to_email or self.settings.digest_to_email
        if not to_email or not self.settings.smtp_host or not self.settings.smtp_user or not self.settings.smtp_password:
            return False
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.settings.smtp_user
        msg["To"] = to_email
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(self.settings.smtp_user, self.settings.smtp_password)
            smtp.sendmail(self.settings.smtp_user, [to_email], msg.as_string())
        return True
