from flask import Blueprint, jsonify, current_app, Response, request
from .. import db
from ..decorators import admin_required
from ..models import Vehicle

vehicles: Blueprint = Blueprint("vehicles", __name__)

@vehicles.route('', methods=['GET'])
@admin_required
def list_vehicles():
    member_id = request.args.get('member_id', type=int)
    if not member_id:
        return jsonify(error="Missing 'member_id'"), 400

    qs = Vehicle.query.filter_by(member_id=member_id).all()
    result = []
    for v in qs:
        # build the same “description” the front‐end expects
        desc = f"{v.year} {v.make} {v.model}"
        result.append({
            "id": v.id,
            "description": desc,
            "passenger_seats": v.passenger_seats
        })

    return jsonify(result), 200

@vehicles.route('', methods=['POST'])
@admin_required
def create_vehicle():
    data = request.get_json() or {}
    member_id = data.get('member_id')
    year = data.get('year')
    make = data.get('make')
    model = data.get('model')
    passenger_seats = data.get('passenger_seats')

    # validate
    if None in (member_id, year, make, model, passenger_seats):
        return jsonify(error="Missing 'member_id', 'description', 'year', 'make', or 'model'"), 400

    # create and save
    v = Vehicle(
        member_id=member_id,
        year=year,
        make=make,
        model=model,
        passenger_seats=int(passenger_seats)
    )
    db.session.add(v)
    db.session.commit()

    return jsonify({
        "id": v.id,
        "description": f"{v.year} {v.make} {v.model}",
        "passenger_seats": v.passenger_seats
    }), 201