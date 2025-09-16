from flask import Blueprint, jsonify, current_app, Response, request
from ..models import Hike, Member, MagicLink, Trail, Vehicle, Signup
from .. import db

hike_signup: Blueprint = Blueprint("hike-signup", __name__)


@hike_signup.route("", methods=["GET", "POST"])
def signup() -> tuple[Response, int]:
    if request.method == "GET":
        token = request.args.get("token")
        if not token:
            return jsonify({"error": "Token is missing"}), 400

        data = current_app.extensions["magic_link_manager"].validate(token)
        status = data["status"]
        if status != "valid":
            return jsonify({"error": "This link is invalid or has expired."}), 400

        mlm = current_app.extensions.get("magic_link_manager")
        if mlm.validate(token)["status"] != "valid":
            return jsonify({"error": "Token is invalid"}), 400

        magic_link = MagicLink.query.filter_by(token=token).first()
        member = Member.query.get(magic_link.member_id)

        hike = Hike.query.get(magic_link.hike_id)
        if hike.phase != "signup":
            return jsonify({"error": "Hike not in signup phase"}), 400

        # check if already signed up
        existing_signup = Signup.query.filter_by(hike_id=hike.id, member_id=member.id).first()
        if existing_signup:
            return jsonify({"status": "signed"}), 200

        trail = Trail.query.get(hike.trail_id)

        vehicles = Vehicle.query.filter_by(member_id=member.id).all()
        vehicles_data = [{
            "id": v.id,
            "make": v.make,
            "model": v.model,
            "year": v.year,
            "passenger_seats": v.passenger_seats
        } for v in vehicles]

        return jsonify({
            "status": "ready",
            "formData": {
                "name": member.name,
                "email": member.email,
                "tel": member.tel,
            },
            "hike": {
                "title": trail.name,
            },
            "vehicles": vehicles_data
        }), 200

    if request.method == "POST":
        # token and hike validations
        token = request.args.get("token")
        if not token:
            return jsonify({"error": "Token is missing"}), 400

        mlm = current_app.extensions.get("magic_link_manager")
        result = mlm.validate(token)
        if result["status"] != "valid":
            return jsonify({"error": "Token is invalid"}), 400

        member = Member.query.get(result["magic_link"].member_id)
        if not member:
            return jsonify({"error": "Member not found"}), 404

        hike = Hike.query.get(result["magic_link"].hike_id)
        if not hike:
            return jsonify({"error": "Hike not found"}), 404

        if hike.status != "active" or hike.phase != "signup":
            return jsonify({"error": "Hike is not open for signup"}), 400

        # check if already signed up
        existing_signup = Signup.query.filter_by(hike_id=hike.id, member_id=member.id).first()
        if existing_signup:
            return jsonify({"error": "Member has already signed up for this hike"}), 400

        # form data validations
        form_data = request.json
        if not form_data:
            return jsonify({"error": "Form data is missing"}), 400

        food_interest = form_data.get("food")
        if food_interest not in ["yes", "no"]:
            return jsonify({"error": "Invalid food interest value"}), 400

        transport_type = form_data.get("transportation")
        if transport_type not in ["is_driver", "is_passenger", "is_self-transport"]:
            return jsonify({"error": "Invalid transportation type"}), 400

        if transport_type == "is_driver" and (form_data.get("vehicle_id") is None):
            return jsonify({"error": "Vehicle information is required for drivers"}), 400

        # phone validation and update
        if not member.tel:
            tel = form_data.get("tel")
            if not tel or not isinstance(tel, str) or len(tel) < 10:
                return jsonify({"error": "A valid phone number is required for this user"}), 400

            tel = "".join([c for c in tel if c.isdigit()])
            if len(tel) < 10:
                return jsonify({"error": "Phone number too short"}), 400

            member.tel = tel
            db.session.commit()

        # transport type branches
        if transport_type == "is_passenger":
            s = Signup(
                hike_id=hike.id,
                member_id=member.id,
                food_interest=(food_interest == "yes"),
                transport_type="passenger"
            )
            db.session.add(s)
            db.session.commit()
            return jsonify({"message": "Successfully signed up as a passenger", "success": True}), 200

        elif transport_type == "is_self-transport":
            s = Signup(
                hike_id=hike.id,
                member_id=member.id,
                food_interest=(food_interest == "yes"),
                transport_type="self"
            )
            db.session.add(s)
            db.session.commit()
            return jsonify({"message": "Successfully signed up as a self-transport", "success": True}), 200

        elif transport_type == "is_driver":
            vehicle_id = form_data.get("vehicle_id")

            if vehicle_id == "new":
                new_vehicle = form_data.get("new_vehicle")
                if not new_vehicle or not isinstance(new_vehicle, dict):
                    return jsonify({"error": "New vehicle information is required"}), 400

                make = new_vehicle.get("make")
                model = new_vehicle.get("model")
                year = new_vehicle.get("year")
                passenger_seats = new_vehicle.get("passenger_seats")

                if not all([make, model, year, passenger_seats]):
                    return jsonify({"error": "Incomplete new vehicle information"}), 400

                try:
                    year = int(year)
                    passenger_seats = int(passenger_seats)
                    if year < 1960 or year > 2100 or passenger_seats < 1 or passenger_seats > 7:  # upward year range is a little more flexible than the fron
                        raise ValueError
                except ValueError:
                    return jsonify({"error": "Invalid year or passenger seats value"}), 400

                vehicle = Vehicle(
                    member_id=member.id,
                    make=make,
                    model=model,
                    year=year,
                    passenger_seats=passenger_seats
                )
                db.session.add(vehicle)
                db.session.commit()
            else:
                vehicle = Vehicle.query.filter_by(id=vehicle_id, member_id=member.id).first()
                if not vehicle:
                    return jsonify({"error": "Selected vehicle not found"}), 404

            s = Signup(
                hike_id=hike.id,
                member_id=member.id,
                food_interest=(food_interest == "yes"),
                transport_type="driver",
                vehicle_id=vehicle.id
            )
            db.session.add(s)
            db.session.commit()
            return jsonify({"message": "Successfully signed up as a driver", "success": True}), 200


@hike_signup.route("/cancel", methods=["GET", "POST"])
def cancel_signup():
    # token and hike validations
    print()
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Token is missing"}), 400

    mlm = current_app.extensions.get("magic_link_manager")
    result = mlm.validate(token)
    if result["status"] != "valid":
        return jsonify({"error": "Token is invalid"}), 400

    member = Member.query.get(result["magic_link"].member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404

    hike = Hike.query.get(result["magic_link"].hike_id)
    if not hike:
        return jsonify({"error": "Hike not found"}), 404

    if hike.status != "active" or hike.phase != "signup":
        return jsonify({"error": "Hike is not open for signup"}), 400

    # check if already signed up
    existing_signup = Signup.query.filter_by(hike_id=hike.id, member_id=member.id).first()
    if not existing_signup:
        return jsonify({"error": "User has not signed up for this hike"}, 400)

    db.session.delete(existing_signup)
    db.session.commit()

    return jsonify({"success": True}, 200)
