"""API views for listing apartments: CRUD, availability toggle, and search stats."""

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsLessor
from apps.listings.dto.apartment_serializers import (
    ApartmentCreateSerializer,
    ApartmentResponseSerializer,
    ApartmentUpdateSerializer,
)
from apps.listings.dto.query_serializers import ListingQuerySerializer
from apps.listings.services.apartment_service import ApartmentService


class ListingListController(APIView):
    """API controller for listing apartments with filters and pagination.

    Also handles creating new listings.
    """

    def get_permissions(self):
        """Determine and return the permission classes based on the HTTP method.

        Returns:
            list: Permission instances required for the request.
        """
        if self.request.method == "POST":
            return [IsAuthenticated(), IsLessor()]
        return [AllowAny()]

    @extend_schema(
        tags=["Listings"],
        summary="List apartments with filters and pagination",
        description="Housing catalog. Supports search, filtering, and sorting.",
        parameters=[ListingQuerySerializer],
        responses={200: ApartmentResponseSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a paginated and filtered list of active apartment listings.

        Args:
            request: The HTTP request object containing query parameters.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A JSON response containing items, page, page_size, and total count.
        """
        query = ListingQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        result = ApartmentService().list_listings(query.validated_data, user=request.user)

        return Response(
            {
                "items": ApartmentResponseSerializer(result["items"], many=True).data,
                "page": result["page"],
                "page_size": result["page_size"],
                "total": result["total"],
            }
        )

    @extend_schema(
        tags=["Listings"],
        summary="Create a listing",
        description="Lessors (LESSOR) only.",
        request=ApartmentCreateSerializer,
        responses={201: ApartmentResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        """Create a new apartment listing owned by the requesting lessor.

        Args:
            request: The HTTP request object containing creation payload.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: Serialized data of the created apartment with status 201 Created.
        """
        serializer = ApartmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        apartment = ApartmentService().create_listing(request.user, serializer.validated_data)

        return Response(
            ApartmentResponseSerializer(apartment).data,
            status=status.HTTP_201_CREATED,
        )


class ListingDetailController(APIView):
    """API controller for retrieving, updating, or deleting a single apartment listing."""

    def get_permissions(self):
        """Determine and return the permission classes based on the HTTP method.

        Returns:
            list: Permission instances required for the request.
        """
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), IsLessor()]
        return [AllowAny()]

    @extend_schema(
        tags=["Listings"],
        summary="Listing details",
        description="Fetch information by ID. Automatically records a view.",
        responses={200: ApartmentResponseSerializer},
    )
    def get(self, request, apartment_id, *args, **kwargs):
        """Retrieve apartment details by ID and record a view metric.

        Args:
            request: The HTTP request object.
            apartment_id (int): The unique identifier of the apartment.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: Serialized apartment detail data.
        """
        apartment = ApartmentService().get_listing(apartment_id, request.user)

        return Response(ApartmentResponseSerializer(apartment).data)

    @extend_schema(
        tags=["Listings"],
        summary="Update a listing",
        description="Listing owner only.",
        request=ApartmentUpdateSerializer,
        responses={200: ApartmentResponseSerializer},
    )
    def patch(self, request, apartment_id, *args, **kwargs):
        """Partially update an existing apartment listing owned by the requesting user.

        Args:
            request: The HTTP request object containing update fields.
            apartment_id (int): The unique identifier of the apartment.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: Serialized updated apartment data.
        """
        serializer = ApartmentUpdateSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        apartment = ApartmentService().update_listing(
            user=request.user,
            apartment_id=apartment_id,
            validated_data=serializer.validated_data,
        )

        return Response(ApartmentResponseSerializer(apartment).data)

    @extend_schema(
        tags=["Listings"],
        summary="Delete a listing",
        description="Owner only.",
        responses={204: OpenApiResponse(description="Listing deleted")},
    )
    def delete(self, request, apartment_id, *args, **kwargs):
        """Delete an apartment listing owned by the requesting user.

        Args:
            request: The HTTP request object.
            apartment_id (int): The unique identifier of the apartment.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: Empty response with status 204 No Content.
        """
        ApartmentService().delete_listing(request.user, apartment_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListingAvailabilityController(APIView):
    """API controller for toggling whether a listing is publicly visible."""

    permission_classes = [IsAuthenticated, IsLessor]
    serializer_class = ApartmentResponseSerializer

    @extend_schema(
        tags=["Listings"],
        summary="Toggle listing visibility",
        description="Turns `is_active` on/off.",
        responses={200: ApartmentResponseSerializer},
    )
    def post(self, request, apartment_id, *args, **kwargs):
        """Flip the `is_active` availability flag on a listing owned by the requesting lessor.

        Args:
            request: The HTTP request object.
            apartment_id (int): The unique identifier of the apartment.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: Serialized apartment data with updated visibility status.
        """
        apartment = ApartmentService().toggle_availability(request.user, apartment_id)
        return Response(ApartmentResponseSerializer(apartment).data)


class MyListingsController(APIView):
    """API controller for retrieving all listings owned by the requesting lessor.

    Includes hidden ones.
    """

    permission_classes = [IsAuthenticated, IsLessor]

    @extend_schema(
        tags=["Listings"],
        summary="My listings",
        description="All listings belonging to the current lessor (including hidden ones).",
        responses={200: ApartmentResponseSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        """Retrieve all active and hidden listings owned by the currently authenticated lessor.

        Args:
            request: The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: Serialized list of apartments owned by the user.
        """
        apartments = ApartmentService().list_my_listings(request.user)
        return Response(ApartmentResponseSerializer(apartments, many=True).data)


class PopularSearchesController(APIView):
    """API controller for exposing the most frequently used search keywords."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Listings"],
        summary="Popular search queries",
        responses={200: {"type": "array", "items": {"type": "object"}}},
    )
    def get(self, request, *args, **kwargs):
        """Retrieve the top popular search keywords.

        Args:
            request: The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A list of popular search queries.
        """
        return Response(ApartmentService().popular_searches())
