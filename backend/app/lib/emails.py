import smtplib
import ssl
from email.message import EmailMessage
from html import escape as _html_escape
from typing import Optional, Sequence
from urllib.parse import quote_plus

from flask import current_app

from ..models import Member, Trail

try:
    # Optional: nicer HTML rendering if 'markdown' is installed.
    import markdown as _markdown_lib  # type: ignore
except Exception:  # pragma: no cover
    _markdown_lib = None


class Emails:
    """
    Simple email utility.

    Required Flask config keys (with reasonable defaults):
      - MAIL_SMTP_HOST (str)
      - MAIL_SMTP_PORT (int)                         [default: 25]
      - MAIL_SMTP_USERNAME (str|None)                [default: None]
      - MAIL_SMTP_PASSWORD (str|None)                [default: None]
      - MAIL_USE_TLS (bool)                          [default: True]
      - MAIL_FROM (str)                              [e.g., "hikingclub@uci.edu"]
      - MAIL_REPLY_TO (str|None)                     [optional]
      - BASE_URL (str)                               [URL of the app in production]

    """

    # ---------- Public API ----------
    @classmethod
    def send_voting_email(
        cls,
        member_id: int,
        token: str,
        subject: Optional[str] = None,
    ) -> bool:
        """
        Voting-phase email to a single member.
        - Generates a single-use magic link token and builds:
            {BASE_URL}/vote?token=<token>
        - Renders minimal boilerplate markdown including:
            - Greeting by member name
            - Magic link button URL (displayed as a plain link in markdown)
            - List of trail options with (difficulty)
        - Calls the base sender and returns True/False.
        """
        # Generate token -> URL
        base_url = current_app.config.get("BASE_URL", "").rstrip("/")
        if not base_url:
            raise RuntimeError("BASE_URL must be set in app config")

        magic_url = f"{base_url}/vote?token={quote_plus(token)}"

        # Member display name
        member = Member.query.get(member_id)
        name = getattr(member, "name", None)
        to_email = getattr(member, "email", None)
        if not to_email:
            raise ValueError("Member object must have an 'email' attribute")

        # Normalize trail options → list of strings like "- Crystal Cove (Difficult)"
        trail_options = Trail.query.filter_by(is_active_vote_candidate=True).all()

        items = [(t.name, current_app.config["DIFFICULTY_INDEX"][t.difficulty]) for t in trail_options]

        # plain-text body
        trails_text = "\n".join([f"- {n}" + (f" ({d})" if d else "") for n, d in items]) or "- (Options forthcoming)"
        text_body = f"""Hi {name},

        It's time to vote for this week's hike! Your voting link is below:

        {magic_url}

        Trail options:
        {trails_text}

        This link is personal to you and expires when voting ends. Please do not share it with others.

        — Hiking Club @ UCI
        """

        # HTML body with inline CSS
        font_stack = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji'"
        trails_html = "".join(
            f"<li style='margin:0 0 6px'>{_html_escape(n)}"
            + (f" <span style=\"color:#6b7280\">({_html_escape(d)})</span>" if d else "")
            + "</li>"
            for n, d in items
        ) or "<li>(Options forthcoming)</li>"

        html_body = f"""\
        <!doctype html>
        <html>
          <body style="margin:0;padding:0;background:#f6f7f9;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f6f7f9;">
              <tr>
                <td align="center" style="padding:24px;">
                  <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                         style="width:600px;max-width:100%;background:#ffffff;border-radius:8px;
                                padding:24px;font-family:{font_stack};color:#111827;">
                    <tr><td>
                      <p style="margin:0 0 12px;">Hi {_html_escape(name)},</p>

                      <p style="margin:0 0 12px;">It’s time to <strong>vote for this week’s hike</strong>! Your single-use link is below:</p>

                      <p style="margin:0 0 20px;">
                        <a href="{_html_escape(magic_url)}"
                           style="display:inline-block;text-decoration:none;padding:12px 18px;border-radius:6px;
                                  background:#1d4ed8;color:#ffffff;font-weight:600;">Vote Here</a>
                      </p>

                      <p style="margin:0 0 8px;"><strong>Trail options</strong>:</p>
                      <ul style="padding-left:20px;margin:0 0 16px;">
                        {trails_html}
                      </ul>

                      <p style="margin:0;color:#6b7280;">
                        This link is personal to you and expires soon. If you didn’t request this, you can ignore this email.
                      </p>

                      <p style="margin:16px 0 0;">— Hike UCI</p>
                    </td></tr>
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """

        subj = subject or "Vote for this week's hike"
        return cls.send_multipart(to=to_email, subject=subj, text_body=text_body, html_body=html_body)

    # ---------- Internal helpers ----------
    @classmethod
    def send_multipart(
            cls, to, subject, text_body, html_body, headers=None, cc=None, bcc=None
    ) -> bool:
        """
        Send a multipart/alternative email with plain text + HTML.
        Returns True/False.
        """
        from email.message import EmailMessage
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
            if cc:
                msg["Cc"] = ", ".join(cc)
            if headers:
                for k, v in headers.items():
                    if k and v: msg[k] = v

            # parts
            msg.set_content(text_body)
            msg.add_alternative(html_body, subtype="html")

            # stash bcc so _smtp_send includes it
            msg._bcc_recipients = list(bcc) if bcc else []  # type: ignore[attr-defined]

            cls._smtp_send(msg=msg)
            return True
        except Exception:
            current_app.logger.exception("Email send failed (subject=%r, to=%r)", subject, to)
            return False

    @classmethod
    def _smtp_send(cls, msg: EmailMessage) -> None:
        """
            Low-level SMTP sender.
            - Reads connection/auth from Flask config.
            - Uses explicit envelope MAIL FROM.
            - Sends multipart message to To/Cc/Bcc recipients.
            - Raises exceptions on failure (caller handles/logs).
            """
        cfg = current_app.config

        host = cfg.get("MAIL_SMTP_HOST")
        if not host:
            raise RuntimeError("MAIL_SMTP_HOST must be set")

        port = int(cfg.get("MAIL_SMTP_PORT", 587))
        username = cfg.get("MAIL_SMTP_USERNAME")
        password = cfg.get("MAIL_SMTP_PASSWORD")
        use_tls = bool(cfg.get("MAIL_USE_TLS", True))
        timeout = float(cfg.get("MAIL_SMTP_TIMEOUT", 30))

        # Collect recipients (To + Cc + hidden Bcc)
        recipients: list[str] = []
        for hdr in ("To", "Cc"):
            if hdr in msg and msg[hdr]:
                recipients.extend([x.strip() for x in str(msg[hdr]).split(",") if x.strip()])
        bcc = getattr(msg, "_bcc_recipients", [])  # set by builder; not a real header
        recipients.extend(bcc or [])

        # De-dup while preserving order
        seen = set()
        recipients = [r for r in recipients if not (r in seen or seen.add(r))]
        if not recipients:
            raise ValueError("No recipients provided")

        # Envelope MAIL FROM (Return-Path) must be explicit
        envelope_from = cfg.get("MAIL_FROM")

        context = ssl.create_default_context()
        with smtplib.SMTP(host=host, port=port, timeout=timeout) as server:
            server.ehlo()
            if use_tls:
                server.starttls(context=context)
                server.ehlo()
            server.login(username, password or "")

            server.send_message(
                msg,
                from_addr=envelope_from,
                to_addrs=list(recipients),
            )