import smtplib
import ssl
from contextlib import contextmanager
from email.message import EmailMessage
from typing import Optional

from flask import current_app


class EmailConnection:
    @contextmanager
    def connect(self):
        """
        Open an SMTP connection with TLS based on Flask config and yield the server.
        Ensures TLS and optional login. Always closes (quit/close) on exit.
        """
        cfg = current_app.config
        if cfg.get("DUMMY_EMAIL_MODE"):
            yield None
            return # no-op in dummy mode
        host = cfg.get("MAIL_SMTP_HOST")
        if not host:
            raise RuntimeError("MAIL_SMTP_HOST must be set")

        port = int(cfg.get("MAIL_SMTP_PORT", 587))
        username = cfg.get("MAIL_SMTP_USERNAME")
        password = cfg.get("MAIL_SMTP_PASSWORD")
        timeout = float(cfg.get("MAIL_SMTP_TIMEOUT", 30))

        context = ssl.create_default_context()
        server = smtplib.SMTP(host=host, port=port, timeout=timeout)
        try:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            if username:  # Some relays are IP-allowed; don't force auth
                server.login(username, password or "")
            yield server
        finally:
            try:
                server.quit()
            except Exception:
                try:
                    server.close()
                except Exception:
                    pass
    def send(self, to, subject, text_body, html_body) -> bool:
        """
        Send a multipart/alternative email with plain text + HTML.
        Returns True/False.
        """
        try:
            msg = EmailMessage()
            cfg = current_app.config
            mail_from = cfg.get("MAIL_FROM")
            if not mail_from:
                raise RuntimeError("MAIL_FROM must be set")

            # headers
            msg["Subject"] = subject
            msg["From"] = mail_from
            msg["To"] = to if isinstance(to, str) else ", ".join(to)

            # parts
            msg.set_content(text_body)
            msg.add_alternative(html_body, subtype="html")

            # Send via SMTP
            if cfg.get("DUMMY_EMAIL_MODE"):
                current_app.logger.info("Dummy email mode: Not sending email content:\n%s", msg)
                return True
            with self.connect() as server:
                self._smtp_send(msg=msg, server=server)
            return True
        except Exception:
            current_app.logger.exception("Email send failed (subject=%r, to=%r)", subject, to)
            return False

    def _smtp_send(self, msg: EmailMessage, *, server: Optional[smtplib.SMTP] = None) -> None:
        """
        Low-level SMTP sender.
        - Reads envelope sender from config.
        - Sends multipart message to To/Cc/Bcc recipients.
        - If `server` is None, opens a connection via `connect()` (fallback).
        """
        cfg = current_app.config

        # Collect recipients (To + Cc + hidden Bcc)
        recipients: list[str] = []
        for hdr in ("To", "Cc"):
            if hdr in msg and msg[hdr]:
                recipients.extend([x.strip() for x in str(msg[hdr]).split(",") if x.strip()])
        bcc = getattr(msg, "_bcc_recipients", [])  # if you ever set it upstream
        recipients.extend(bcc or [])

        # De-dup while preserving order
        seen = set()
        recipients = [r for r in recipients if not (r in seen or seen.add(r))]
        if not recipients:
            raise ValueError("No recipients provided")

        # Envelope MAIL FROM (Return-Path) — keep your current behavior
        envelope_from = cfg.get("MAIL_FROM")

        server.send_message(
            msg,
            from_addr=envelope_from,
            to_addrs=list(recipients),
        )
