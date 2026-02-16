from math import radians, sin, cos, sqrt, atan2


class PricingService:

    BASE_FARE = 100
    PER_KM_RATE = 15

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km

        dlat = radians(float(lat2) - float(lat1))
        dlon = radians(float(lon2) - float(lon1))

        a = sin(dlat/2)**2 + cos(radians(float(lat1))) * \
            cos(radians(float(lat2))) * sin(dlon/2)**2

        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    @staticmethod
    def calculate_price(ride, ride_request):

        # 1️⃣ Distance based pricing
        distance = PricingService.calculate_distance(
            ride_request.pickup_lat,
            ride_request.pickup_lng,
            ride_request.drop_lat,
            ride_request.drop_lng
        )

        base_price = PricingService.BASE_FARE + (distance * PricingService.PER_KM_RATE)

        # 2️⃣ Occupancy surge
        occupancy_ratio = (
            (ride.total_seats - ride.available_seats) / ride.total_seats
        )

        surge_multiplier = 1.0

        if occupancy_ratio > 0.7:
            surge_multiplier = 1.2
        elif occupancy_ratio > 0.4:
            surge_multiplier = 1.1

        final_price = base_price * surge_multiplier

        return round(final_price, 2)
