from typing import Tuple, Any
from flask import render_template
from jinja2 import Environment, FileSystemLoader, FileSystemBytecodeCache
from .email_utils import flatten_num
from .. import db
from ..models import Trail, Hike
from flask import current_app

env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=True,
    bytecode_cache=FileSystemBytecodeCache(directory="app/templates/.j2cache")
)

EMAIL_SUBJECTS = {
    "voting": "Vote for this week's hike",
    "signup": "Sign up for this week's hike",
    "waiver": "Complete your hike waiver",
    "waiver_confirmation": "Completed: Your hike waiver"
}


def render_email_batch(email_type, hike: Hike):
    """
    Compute batch context once (DB lookups, queries, markdown -> HTML, etc.) then render
    """

    batch = {}

    if email_type == "voting":
        trail_options = Trail.query.filter_by(is_active_vote_candidate=True).all()
        batch["trails"] = [{"name": t.name,
                            "difficulty": current_app.config["DIFFICULTY_INDEX"][t.difficulty]}
                           for t in trail_options]

        return _render_email_batch(email_type, batch)

    # Common data for signup / waiver email types
    trail = Trail.query.get(hike.trail_id)

    batch["hike_day"] = hike.hike_date.strftime("%A %-m/%-d")
    batch["hike_time"] = hike.hike_date.strftime("%-I:%M %p")
    batch["hike_trail_name"] = trail.name
    batch["hike_town_name"] = trail.location
    batch["hike_length_mi"] = flatten_num(trail.length_mi)
    batch["hike_estimated_time_hr"] = flatten_num(trail.estimated_time_hr)
    batch["hike_difficulty"] = current_app.config["DIFFICULTY_INDEX"][trail.difficulty]
    batch["num_liters"] = flatten_num(trail.required_water_liters)
    batch["description"] = trail.description

    if email_type == "signup":
        # good to go
        return _render_email_batch(email_type, batch)

    elif email_type in ["waiver", "waiver_confirmation"]:
        # added data
        batch["hike_trail_gmap_link"] = trail.trailhead_gmaps_endpoint
        batch["hike_trail_amap_link"] = trail.trailhead_amaps_endpoint

        return _render_email_batch(email_type, batch)

    else:
        raise ValueError(f"Email type {email_type} not recognized")


def _render_email_batch(email_type: str, batch: dict) -> Tuple:
    subject = EMAIL_SUBJECTS.get(email_type)
    text_body = env.get_template(f"email/{email_type}.txt.j2")
    html_body = env.get_template(f"email/{email_type}.html.j2")

    text_body_mod = text_body.make_module({"batch": batch})
    html_body_mod = html_body.make_module({"batch": batch})

    return subject, text_body_mod, html_body_mod, batch
