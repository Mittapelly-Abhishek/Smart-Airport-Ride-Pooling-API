"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rides.views import CreateRideView
from bookings.views import CreateRideRequestView
from bookings.views import CancelBookingView
from rides.views import ActiveRidesView
from rides.views import RideDetailView



from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    
    def get(self, request):
        return Response({"status": "OK"})


schema_view = get_schema_view(
    openapi.Info(
        title="Smart Airport Ride Pooling API",
        default_version='v1',
        description="API documentation for Smart Airport Ride Pooling Backend",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/rides/', CreateRideView.as_view()),
    path('api/requests/', CreateRideRequestView.as_view()),
    path('api/bookings/<int:booking_id>/cancel/', CancelBookingView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('api/health/', HealthCheckView.as_view()),
    path('api/rides/active/', ActiveRidesView.as_view()),
    path('api/rides/<int:ride_id>/', RideDetailView.as_view()),


]
