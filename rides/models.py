from django.db import models
from django.db.models import Index


class Ride(models.Model):

    STATUS_CHOICES = (
        ("SEARCHING", "SEARCHING"),
        ("FULL", "FULL"),
        ("STARTED", "STARTED"),
        ("CANCELLED", "CANCELLED"),
    )

    driver_id = models.BigIntegerField(db_index=True)

    # Origin (Airport or pickup start)
    origin_lat = models.DecimalField(max_digits=9, decimal_places=6)
    origin_lng = models.DecimalField(max_digits=9, decimal_places=6)

    # Destination
    destination_lat = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = models.DecimalField(max_digits=9, decimal_places=6)

    total_seats = models.IntegerField()
    available_seats = models.IntegerField(db_index=True)

    total_luggage_capacity = models.IntegerField()
    available_luggage_capacity = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SEARCHING",
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
        models.Index(fields=["status", "available_seats", "available_luggage_capacity"]),
    ]


    def __str__(self):
        return f"Ride {self.id} - {self.status}"
