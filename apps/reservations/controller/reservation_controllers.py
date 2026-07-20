"""API views for creating and managing reservations through their lifecycle.

This module contains DRF API views to handle reservation creation, status
transitions (confirmation, check-in, cancellation), and listing user reservations
from both renter and lessor perspectives.
"""

from drf_spectacular.utils import extend_schema
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
    """Create a new reservation for a listing."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reservations"],
        summary="Create a reservation",
        description="Renters only. Checks date availability and overlaps.",
        request=ReservationCreateSerializer,
        responses={201: ReservationResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        """Create a reservation for the requesting renter after validating dates."""
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
    """Confirm a pending reservation."""

    permission_classes = [IsAuthenticated]
    serializer_class = ReservationResponseSerializer

    @extend_schema(
        tags=["Reservations"],
        summary="Confirm a reservation",
        description="Lessor only. Transitions status PENDING → CONFIRMED.",
        responses={200: ReservationResponseSerializer},
    )
    def patch(self, request, reservation_id, *args, **kwargs):
        """Move a reservation from PENDING to CONFIRMED."""
        reservation = ReservationService().confirm_reservation(request.user, reservation_id)
        return Response(ReservationResponseSerializer(reservation).data)


class ReservationCheckInController(APIView):
    """Mark a confirmed reservation as checked in."""

    permission_classes = [IsAuthenticated]
    serializer_class = ReservationResponseSerializer

    @extend_schema(
        tags=["Reservations"],
        summary="Mark check-in",
        description="Lessor only. Transitions status CONFIRMED → CHECKED_IN.",
        responses={200: ReservationResponseSerializer},
    )
    def patch(self, request, reservation_id, *args, **kwargs):
        """Move a reservation from CONFIRMED to CHECKED_IN."""
        reservation = ReservationService().check_in_reservation(request.user, reservation_id)
        return Response(ReservationResponseSerializer(reservation).data)


class ReservationCancelController(APIView):
    """Cancel a reservation."""

    permission_classes = [IsAuthenticated]
    serializer_class = ReservationResponseSerializer

    @extend_schema(
        tags=["Reservations"],
        summary="Cancel a reservation",
        description="Available to either the renter or the lessor (subject to rule checks).",
        responses={200: ReservationResponseSerializer},
    )
    def patch(self, request, reservation_id, *args, **kwargs):
        """Cancel a reservation, enforcing renter/lessor transition rules."""
        reservation = ReservationService().cancel_reservation(request.user, reservation_id)
        return Response(ReservationResponseSerializer(reservation).data)


class MyReservationsController(APIView):
    """List reservations made by the requesting user as a renter."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reservations"],
        summary="My reservations (as renter)",
        responses={200: ReservationResponseSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        """Return all reservations made by the current user as a renter."""
        reservations = ReservationService().get_my_reservations(request.user)
        return Response(ReservationResponseSerializer(reservations, many=True).data)


class LessorReservationsController(APIView):
    """List reservations made on the requesting user's listings as a lessor."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reservations"],
        summary="Reservations on my listings (as lessor)",
        responses={200: ReservationResponseSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        """Return all reservations made on listings owned by the current lessor."""
        reservations = ReservationService().get_lessor_reservations(request.user)
        return Response(ReservationResponseSerializer(reservations, many=True).data)
