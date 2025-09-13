import random
from typing import List
from ..models import Hike, Signup, Vehicle


def run(hike_id: int) -> tuple[List[int], List[int]]:
    current_hike = Hike.query.get(hike_id)
    confirmed: List[int] = []
    waitlisted: List[int] = []

    pending_drivers = Signup.query.filter_by(hike_id=hike_id, status="pending", transport_type="driver").all()
    pending_selfs = Signup.query.filter_by(hike_id=hike_id, status="pending", transport_type="self").all()
    pending_passengers = Signup.query.filter_by(hike_id=hike_id, status="pending", transport_type="passenger").all()

    past_hikes = (Hike.query
                  .filter(Hike.hike_date < current_hike.hike_date)
                  .order_by(Hike.hike_date.desc())
                  .limit(2)
                  .all()
                  )

    passenger_capacity = sum([Vehicle.query.get(d.vehicle_id).passenger_capacity for d in pending_drivers])
    print(passenger_capacity)

    # drivers and self-transports are always confirmed
    confirmed += [d.id for d in pending_drivers]
    confirmed += [s.id for s in pending_selfs]

    if passenger_capacity >= len(pending_passengers):
        # we have enough capacity for everyone
        confirmed += [p.id for p in pending_passengers]
    else:
        # determine who goes on the waitlist
        if len(past_hikes) == 0:
            # no past hike data available, randomly assign to waitlist
            while len(pending_passengers) > 0:
                chosen_passenger = pending_passengers.pop(random.randrange(len(pending_passengers)))
                if passenger_capacity > 0:
                    confirmed.append(chosen_passenger)
                    passenger_capacity -= 1
                else:
                    waitlisted.append(chosen_passenger)

        elif len(past_hikes) == 1:
            # only data available from 1 previous hike
            last_id = past_hikes[0].id

            # Group passengers by whether they attended the last hike
            never_last = []
            did_last = []

            for p in list(pending_passengers):  # iterate over a copy
                went_last = Signup.query.filter_by(member_id=p.id, hike_id=last_id).first() is not None
                if went_last:
                    did_last.append(p)
                else:
                    never_last.append(p)

            # Randomize within priority groups
            random.shuffle(never_last)
            random.shuffle(did_last)

            # Priority: never_last -> did_last
            ordered = never_last + did_last

            for p in ordered:
                if passenger_capacity > 0:
                    confirmed.append(p)
                    passenger_capacity -= 1
                else:
                    waitlisted.append(p)

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
                went_last = Signup.query.filter_by(member_id=p.id, hike_id=last_id).first() is not None
                went_two_ago = Signup.query.filter_by(member_id=p.id, hike_id=two_ago_id).first() is not None

                if not went_last and not went_two_ago:
                    missed_both.append(p)
                elif not went_last and went_two_ago:
                    missed_last_attended_two_ago.append(p)
                else:
                    attended_last.append(p)

            # Randomize within priorities
            random.shuffle(missed_both)
            random.shuffle(missed_last_attended_two_ago)
            random.shuffle(attended_last)

            ordered = missed_both + missed_last_attended_two_ago + attended_last

            for p in ordered:
                if passenger_capacity > 0:
                    confirmed.append(p)
                    passenger_capacity -= 1
                else:
                    waitlisted.append(p)

            pending_passengers.clear()

    return confirmed, waitlisted

