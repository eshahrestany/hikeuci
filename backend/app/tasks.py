from urllib.parse import quote_plus
from flask import current_app
from backend.app.models import Member, Trail
from html import escape as _html_escape

def batch_send_vote_email():
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

    trail_options = Trail.query.filter_by(is_active_vote_candidate=True).all()
    items = [(t.name, current_app.config["DIFFICULTY_INDEX"][t.difficulty]) for t in trail_options]

    # plain-text body
    trails_text = "\n".join([f"- {n}" + (f" ({d})" if d else "") for n, d in items])

    subj = "Vote for this week's hike"

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