from django.urls import path, include
from rest_framework.routers import DefaultRouter
from transactions.views import (
    CategoryModelViewSet,
    DescriptionModelViewSet,
    TransactionModelViewSet
)


router = DefaultRouter()
router.register('categories', CategoryModelViewSet)
router.register('descriptions', DescriptionModelViewSet)
router.register('transactions', TransactionModelViewSet)

urlpatterns = [
    path('', include(router.urls))
]
