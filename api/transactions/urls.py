from django.urls import path, include
from rest_framework.routers import DefaultRouter
from transactions.views import *

router = DefaultRouter()
router.register('groups', GroupModelViewSet)
router.register('descriptions', DescriptionModelViewSet)
router.register('transactions', TransactionModelViewSet)
router.register('recurring', RecurringModelViewSet)

urlpatterns = [
    path('', include(router.urls))
]