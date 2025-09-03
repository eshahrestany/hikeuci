from typing import Tuple, Any
from flask import render_template

EMAIL_SUBJECTS = {
    "voting": "Vote for this week's hike",
    "signup": "Sign up for this week's hike",
    "waiver": "Complete your hike waiver",
}


def render_phase_email(phase: str, **context: Any) -> Tuple[str, str, str]:
    """
    Renders subject, text, and html bodies for a given phase.
    Expects templates at: templates/{phase}.txt.j2 or .html.j2
    Context should include: name, magic_url, trails (list[{name,difficulty}]), etc.
    """
    subject = EMAIL_SUBJECTS.get(phase)
    text_body = render_template(f"{phase}.txt.j2", **context)
    html_body = render_template(f"{phase}.html.j2", **context)
    return subject, text_body, html_body
