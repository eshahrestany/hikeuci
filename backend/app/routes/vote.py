from flask import Blueprint, request, jsonify, current_app
from .. import db
from ..models import Member, Hike, Trail, MagicLink, Vote

hike_vote: Blueprint = Blueprint("hike-vote", __name__)

@hike_vote.route("", methods=["GET", "POST"])
def hike_vote_page():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Token is missing"}), 400

    data = current_app.extensions["magic_link_manager"].validate(token)
    status = data["status"]
    if status != "valid":
        return jsonify({"error": "This link is invalid or has expired."}), 400

    magic_link = MagicLink.query.filter_by(token=token).first()
    member = Member.query.get(magic_link.member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    if request.method == "GET":
        hike = Hike.query.filter_by(id=magic_link.hike_id).first()
        existing_vote = Vote.query.filter_by(member_id=member.id, hike_id=hike.id).first()
        if existing_vote: existing_vote = existing_vote.trail_id

        trail_opts = Trail.query.filter_by(is_active_vote_candidate=True)
        counts = {t.id: Vote.query.filter_by(trail_id=t.id).count() for t in trail_opts}
        trails = []
        for trail in trail_opts:
            trails.append({
                "id": trail.id,
                "name": trail.name,
                "location": trail.location,
                "length_mi": trail.length_mi,
                "estimated_time_hr": trail.estimated_time_hr,
                "difficulty": current_app.config.get("DIFFICULTY_INDEX").get(trail.difficulty)
            })

        payload = {
            "ends_at": hike.signup_date,
            "trails": trails,
            "counts": counts,
            "user_vote_trail_id": existing_vote
        }

        return jsonify(payload), 200

    elif request.method == "POST":
        vote_trail_id = request.json.get("trail_id")
        trail = Trail.query.get(vote_trail_id)
        if not trail:
            return jsonify({"error": "Trail not found"}), 404

        hike = Hike.query.filter_by(id=magic_link.hike_id).first()
        existing_vote = Vote.query.filter_by(member_id=member.id, hike_id=hike.id).first()
        if existing_vote:
            existing_vote.trail_id = vote_trail_id
            db.session.commit()
            return jsonify({"success": True}), 200

        vote = Vote(
            member_id=member.id,
            hike_id=hike.id,
            trail_id=vote_trail_id
        )
        db.session.add(vote)
        db.session.commit()
        return jsonify({"success": True}), 200
