from typing import List
from ..models import Hike, Signup, Vehicle
from typing import List

from ..models import Hike, Signup, Vehicle



def calc_passenger_capacity(drivers: List[Signup]) -> int:
    """Returns a list of signup ids to set as confirmed, and a list of signup ids to set as waitlisted in order
    (first item is first on the waistlist)"""
    vehicle_ids = [d.vehicle_id for d in drivers if d.vehicle_id]
    if not vehicle_ids:
        return 0
    vehicles = Vehicle.query.filter(Vehicle.id.in_(vehicle_ids)).all()
    cap_by_id = {v.id: v.passenger_seats for v in vehicles}
    return sum(cap_by_id.get(d.vehicle_id, 0) for d in drivers)


def run(hike_id: int) -> tuple[List[int], List[int]]:
    current_hike = Hike.query.get(hike_id)
    confirmed: List[int] = []
    waitlisted: List[int] = []

    pending_drivers = Signup.query.filter_by(hike_id=hike_id, status="pending", transport_type="driver").all()
    pending_selfs = Signup.query.filter_by(hike_id=hike_id, status="pending", transport_type="self").all()
    pending_passengers = (Signup.query
                          .filter_by(hike_id=hike_id, status="pending", transport_type="passenger")
                          .order_by(Signup.signup_date.asc())
                          .all()
                          )

    past_hikes = (Hike.query
                  .filter(Hike.hike_date < current_hike.hike_date)
                  .filter(Hike.id != current_hike.id)
                  .order_by(Hike.hike_date.desc())
                  .limit(2)
                  .all()
                  )

    passenger_capacity = calc_passenger_capacity(pending_drivers)

    # drivers and self-transports are always confirmed
    confirmed += [d.id for d in pending_drivers]
    confirmed += [s.id for s in pending_selfs]

    if passenger_capacity >= len(pending_passengers):
        # we have enough capacity for everyone
        confirmed += [p.id for p in pending_passengers]
    else:
        # determine who goes on the waitlist
        if len(past_hikes) == 0:
            # no past hike data available, assign by signup time
            while len(pending_passengers) > 0:
                chosen_passenger = pending_passengers.pop(0)
                if passenger_capacity > 0:
                    confirmed.append(chosen_passenger.id)
                    passenger_capacity -= 1
                else:
                    waitlisted.append(chosen_passenger.id)

        elif len(past_hikes) == 1:
            # only data available from 1 previous hike
            last_id = past_hikes[0].id

            # Group passengers by whether they attended the last hike
            never_last = []
            did_last = []

            for p in list(pending_passengers):  # iterate over a copy
                went_last = Signup.query.filter_by(member_id=p.member_id, hike_id=last_id).first() is not None
                if went_last:
                    did_last.append(p)
                else:
                    never_last.append(p)

            # Priority: never_last -> did_last
            ordered = never_last + did_last

            for p in ordered:
                if passenger_capacity > 0:
                    confirmed.append(p.id)
                    passenger_capacity -= 1
                else:
                    waitlisted.append(p.id)

            pending_passengers.clear()

        elif len(past_hikes) == 2:
            last_id = past_hikes[0].id  # most recent (previous) hike
            two_ago_id = past_hikes[1].id  # two hikes ago

            # Priorities:
            # 1) missed both last and two-ago
            # 2) missed last but attended two-ago
            # 3) attended last (regardless of two-ago)
            missed_both = []
            missed_last_attended_two_ago = []
            attended_last = []

            for p in list(pending_passengers):
                went_last = Signup.query.filter_by(member_id=p.member_id, hike_id=last_id).first() is not None
                went_two_ago = Signup.query.filter_by(member_id=p.member_id, hike_id=two_ago_id).first() is not None

                if not went_last and not went_two_ago:
                    missed_both.append(p)
                elif not went_last and went_two_ago:
                    missed_last_attended_two_ago.append(p)
                else:
                    attended_last.append(p)

            ordered = missed_both + missed_last_attended_two_ago + attended_last

            for p in ordered:
                if passenger_capacity > 0:
                    confirmed.append(p.id)
                    passenger_capacity -= 1
                else:
                    waitlisted.append(p.id)

            pending_passengers.clear()

    return confirmed, waitlisted

