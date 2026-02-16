from django.db import models


class RideRequest(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("MATCHED", "MATCHED"),
        ("CANCELLED", "CANCELLED"),
    )

    user_id = models.BigIntegerField(db_index=True)

    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6)

    drop_lat = models.DecimalField(max_digits=9, decimal_places=6)
    drop_lng = models.DecimalField(max_digits=9, decimal_places=6)

    seats_required = models.IntegerField()
    luggage_required = models.IntegerField()

    detour_tolerance_km = models.FloatField(default=5)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request {self.id} - {self.status}"


from rides.models import Ride


class Booking(models.Model):

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="bookings",
        db_index=True
    )

    request = models.OneToOneField(
        RideRequest,
        on_delete=models.CASCADE,
        related_name="booking"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - Ride {self.ride.id}"
