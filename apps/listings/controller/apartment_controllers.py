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

_TAG = "Объявления"


class ListingListController(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsLessor()]
        return [AllowAny()]

    def get(self, request):
        query = ListingQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        result = ApartmentService().list_listings(
            query.validated_data, user=request.user
        )
        return Response(
            {
                "items": ApartmentResponseSerializer(result["items"], many=True).data,
                "page": result["page"],
                "page_size": result["page_size"],
                "total": result["total"],
            }
        )

    def post(self, request):
        serializer = ApartmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        apartment = ApartmentService().create_listing(
            request.user, serializer.validated_data
        )
        return Response(
            ApartmentResponseSerializer(apartment).data,
            status=status.HTTP_201_CREATED,
        )


class ListingDetailController(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), IsLessor()]
        return [AllowAny()]

    def get(self, request, apartment_id):
        apartment = ApartmentService().get_listing(apartment_id, request.user)
        return Response(ApartmentResponseSerializer(apartment).data)

    def patch(self, request, apartment_id):
        serializer = ApartmentUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        apartment = ApartmentService().update_listing(
            user=request.user,
            apartment_id=apartment_id,
            validated_data=serializer.validated_data,
        )

        return Response(ApartmentResponseSerializer(apartment).data)

    def delete(self, request, apartment_id):
        ApartmentService().delete_listing(request.user, apartment_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListingAvailabilityController(APIView):
    permission_classes = [IsAuthenticated, IsLessor]

    def post(self, request, apartment_id):
        apartment = ApartmentService().toggle_availability(request.user, apartment_id)
        return Response(ApartmentResponseSerializer(apartment).data)


class MyListingsController(APIView):
    permission_classes = [IsAuthenticated, IsLessor]

    def get(self, request):
        apartments = ApartmentService().list_my_listings(request.user)
        return Response(ApartmentResponseSerializer(apartments, many=True).data)


class PopularSearchesController(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(ApartmentService().popular_searches())
