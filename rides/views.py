from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from .models import Ride
from .serializers import RideSerializer


class ActiveRidesView(APIView):

    def get(self, request):

        rides = Ride.objects.filter(
            status="SEARCHING",
            available_seats__gt=0
        )

        serializer = RideSerializer(rides, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RideDetailView(APIView):

    def get(self, request, ride_id):

        try:
            ride = Ride.objects.get(id=ride_id)
        except Ride.DoesNotExist:
            return Response(
                {"error": "Ride not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RideSerializer(ride)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateRideView(APIView):

    @swagger_auto_schema(request_body=RideSerializer)
    def post(self, request):

        serializer = RideSerializer(data=request.data)

        if serializer.is_valid():
            ride = serializer.save(
                available_seats=request.data.get("total_seats"),
                available_luggage_capacity=request.data.get("total_luggage_capacity")
            )

            return Response(
                RideSerializer(ride).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
