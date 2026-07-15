from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.reservations.dto.reservation_serializers import (
    ReservationCreateSerializer,
    ReservationResponseSerializer,
)
from apps.reservations.services.reservation_service import ReservationService


class ReservationCreateController(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation = ReservationService().create_reservation(
            request.user, serializer.validated_data
        )
        return Response(
            ReservationResponseSerializer(reservation).data,
            status=status.HTTP_201_CREATED,
        )


class ReservationConfirmController(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, reservation_id, *args, **kwargs):
        reservation = ReservationService().confirm_reservation(
            request.user, reservation_id
        )
        return Response(ReservationResponseSerializer(reservation).data)


class ReservationCheckInController(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, reservation_id, *args, **kwargs):
        reservation = ReservationService().check_in_reservation(
            request.user, reservation_id
        )
        return Response(ReservationResponseSerializer(reservation).data)


class ReservationCancelController(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, reservation_id, *args, **kwargs):
        reservation = ReservationService().cancel_reservation(
            request.user, reservation_id
        )
        return Response(ReservationResponseSerializer(reservation).data)


class MyReservationsController(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        reservations = ReservationService().get_my_reservations(request.user)
        return Response(ReservationResponseSerializer(reservations, many=True).data)


class LessorReservationsController(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        reservations = ReservationService().get_lessor_reservations(request.user)
        return Response(ReservationResponseSerializer(reservations, many=True).data)
