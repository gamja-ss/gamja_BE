from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Coin
from .serializers import CoinSerializer


class UserTotalCoinsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["coin"],
        summary="사용자의 전체 코인 수 조회",
        description="현재 로그인한 사용자의 총 코인 수를 조회합니다.",
        responses={
            200: OpenApiResponse(
                OpenApiTypes.INT,
                description="사용자의 총 코인 수",
                examples=[
                    OpenApiExample(
                        "Successful Response",
                        value={"total_coins": 100},
                        response_only=True,
                    )
                ],
            ),
        },
    )
    def get(self, request):
        total_coins = request.user.total_coins
        return Response({"total_coins": total_coins})


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = None
    max_page_size = 20


class UserCoinLogView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CoinSerializer
    pagination_class = CustomPagination

    @extend_schema(
        tags=["coin"],
        summary="사용자의 코인 로그 조회",
        description="현재 로그인한 사용자의 코인 획득/사용 로그를 페이지네이션(20개씩)하여 조회합니다.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="페이지 번호",
                default=1,
            ),
        ],
        responses={200: CoinSerializer(many=True)},
    )
    def get(self, request):
        queryset = Coin.objects.filter(user=request.user).order_by("-timestamp")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
