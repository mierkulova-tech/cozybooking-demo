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
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsLessor()]
        return [AllowAny()]

    @extend_schema(
        tags=["Listings"],
        summary="Список объявлений с фильтрами и пагинацией",
        description="Каталог жилья. Поддерживает поиск, фильтры и сортировку.",
        parameters=[ListingQuerySerializer],
        responses={200: ApartmentResponseSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
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

    @extend_schema(
        tags=["Listings"],
        summary="Создать объявление",
        description="Только для арендодателей (LESSOR).",
        request=ApartmentCreateSerializer,
        responses={201: ApartmentResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
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

    @extend_schema(
        tags=["Listings"],
        summary="Детали объявления",
        description="Получить информацию по ID. Автоматически фиксирует просмотр.",
        responses={200: ApartmentResponseSerializer},
    )
    def get(self, request, apartment_id, *args, **kwargs):
        apartment = ApartmentService().get_listing(apartment_id, request.user)

        return Response(ApartmentResponseSerializer(apartment).data)

    @extend_schema(
        tags=["Listings"],
        summary="Обновить объявление",
        description="Только владелец объявления.",
        request=ApartmentUpdateSerializer,
        responses={200: ApartmentResponseSerializer},
    )
    def patch(self, request, apartment_id, *args, **kwargs):
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
        summary="Удалить объявление",
        description="Только владелец.",
        responses={204: OpenApiResponse(description="Объявление удалено")},
    )
    def delete(self, request, apartment_id, *args, **kwargs):
        ApartmentService().delete_listing(request.user, apartment_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListingAvailabilityController(APIView):
    permission_classes = [IsAuthenticated, IsLessor]
    serializer_class = ApartmentResponseSerializer

    @extend_schema(
        tags=["Listings"],
        summary="Переключить видимость объявления",
        description="Включает/выключает `is_active`.",
        responses={200: ApartmentResponseSerializer},
    )
    def post(self, request, apartment_id, *args, **kwargs):
        apartment = ApartmentService().toggle_availability(request.user, apartment_id)
        return Response(ApartmentResponseSerializer(apartment).data)


class MyListingsController(APIView):
    permission_classes = [IsAuthenticated, IsLessor]

    @extend_schema(
        tags=["Listings"],
        summary="Мои объявления",
        description="Список всех объявлений текущего арендодателя (включая скрытые).",
        responses={200: ApartmentResponseSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        apartments = ApartmentService().list_my_listings(request.user)
        return Response(ApartmentResponseSerializer(apartments, many=True).data)


class PopularSearchesController(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Listings"],
        summary="Популярные поисковые запросы",
        responses={200: {"type": "array", "items": {"type": "object"}}},
    )
    def get(self, request, *args, **kwargs):
        return Response(ApartmentService().popular_searches())
