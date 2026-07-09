from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reservations.dto.reservation_serializers import (
    ReservationCreateSerializer,
    ReservationResponseSerializer,
    ReservationStatusUpdateSerializer,
)
from apps.reservations.services.reservation_service import ReservationService

_TAG = "Бронирования"


class ReservationCreateController(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation = ReservationService().create_reservation(
            request.user, serializer.validated_data
        )
        return Response(
            ReservationResponseSerializer(reservation).data,
            status=status.HTTP_201_CREATED,
        )


class MyReservationsController(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reservations = ReservationService().get_my_reservations(request.user)
        return Response(ReservationResponseSerializer(reservations, many=True).data)


class LessorReservationsController(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reservations = ReservationService().get_lessor_reservations(request.user)
        return Response(ReservationResponseSerializer(reservations, many=True).data)


class ReservationStatusController(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, reservation_id):
        serializer = ReservationStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation = ReservationService().update_status(
            request.user, reservation_id, serializer.validated_data["status"]
        )
        return Response(ReservationResponseSerializer(reservation).data)
