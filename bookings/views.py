from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from math import radians, sin, cos, sqrt, atan2

from .models import RideRequest, Booking
from .serializers import RideRequestSerializer
from rides.models import Ride
from services.pricing_service import PricingService
from drf_yasg.utils import swagger_auto_schema



# ----------------------------
# Utility: Distance Calculator
# ----------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    dlat = radians(float(lat2) - float(lat1))
    dlon = radians(float(lon2) - float(lon1))

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(float(lat1)))
        * cos(radians(float(lat2)))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


# ============================================
# Create Ride Request + Smart Matching + Book
# ============================================
class CreateRideRequestView(APIView):
    
    @swagger_auto_schema(request_body=RideRequestSerializer)
    @transaction.atomic
    def post(self, request):

        serializer = RideRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Save Ride Request
        ride_request = serializer.save()


        # Step 2: Find candidate rides (Optimized for performance)
        candidate_rides = Ride.objects.filter(
            status="SEARCHING",
            available_seats__gte=ride_request.seats_required,
            available_luggage_capacity__gte=ride_request.luggage_required
        ).only(
                "id",
                "origin_lat",
                "origin_lng",
                "available_seats",
                "available_luggage_capacity",
                "total_seats",
                 "status"
        )[:50]


        best_ride = None
        min_detour = float("inf")

        # Step 3: Smart detour-based selection
        for ride in candidate_rides:

            detour = calculate_distance(
                ride.origin_lat,
                ride.origin_lng,
                ride_request.pickup_lat,
                ride_request.pickup_lng
            )

            if detour <= ride_request.detour_tolerance_km and detour < min_detour:
                best_ride = ride
                min_detour = detour

        if not best_ride:
            return Response(
                {"message": "No ride found within detour tolerance"},
                status=status.HTTP_200_OK
            )

        # Step 4: Lock selected ride row
        matching_ride = Ride.objects.select_for_update().get(id=best_ride.id)

        # Double-check seats after locking (important for concurrency)
        if (
            matching_ride.available_seats < ride_request.seats_required
            or matching_ride.available_luggage_capacity < ride_request.luggage_required
        ):
            return Response(
                {"message": "Ride no longer available"},
                status=status.HTTP_409_CONFLICT
            )

        # Step 5: Calculate dynamic price
        calculated_price = PricingService.calculate_price(
            matching_ride,
            ride_request
        )

        # Step 6: Deduct seats & luggage
        matching_ride.available_seats -= ride_request.seats_required
        matching_ride.available_luggage_capacity -= ride_request.luggage_required

        if matching_ride.available_seats == 0:
            matching_ride.status = "FULL"

        matching_ride.save()

        # Step 7: Create booking
        booking = Booking.objects.create(
            ride=matching_ride,
            request=ride_request,
            price=calculated_price
        )

        # Step 8: Update request status
        ride_request.status = "MATCHED"
        ride_request.save()

        return Response(
            {
                "message": "Ride booked successfully",
                "booking_id": booking.id,
                "ride_id": matching_ride.id,
                "price": calculated_price,
                "detour_km": round(min_detour, 2)
            },
            status=status.HTTP_201_CREATED
        )


# ============================
# Cancel Booking (Atomic Safe)
# ============================
class CancelBookingView(APIView):

    @transaction.atomic
    def post(self, request, booking_id):

        try:
            booking = Booking.objects.select_for_update().get(id=booking_id)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        ride = Ride.objects.select_for_update().get(id=booking.ride.id)

        # Restore seats
        ride.available_seats += booking.request.seats_required
        ride.available_luggage_capacity += booking.request.luggage_required

        if ride.status == "FULL":
            ride.status = "SEARCHING"

        ride.save()

        # Update request status
        booking.request.status = "CANCELLED"
        booking.request.save()

        # Delete booking
        booking.delete()

        return Response(
            {"message": "Booking cancelled successfully"},
            status=status.HTTP_200_OK
        )
