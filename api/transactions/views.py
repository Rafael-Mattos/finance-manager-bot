from dj_rql.drf import RQLFilterBackend
from rest_framework import viewsets
from transactions.filters import (GroupFilterClass, 
                                  DescriptionFilterClass, 
                                  TransactionFilterClass, 
                                  RecurringFilterClass
                                  )
from transactions.models import *
from transactions.serializers import *

class GroupModelViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupModelSerializer
    filter_backends = [RQLFilterBackend]
    rql_filter_class = GroupFilterClass


class DescriptionModelViewSet(viewsets.ModelViewSet):
    queryset = Description.objects.all()
    serializer_class = DescriptionModelSerializer
    filter_backends = [RQLFilterBackend]
    rql_filter_class = DescriptionFilterClass


class TransactionModelViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionModelSerializer
    filter_backends = [RQLFilterBackend]
    rql_filter_class = TransactionFilterClass


class RecurringModelViewSet(viewsets.ModelViewSet):
    queryset = Recurring.objects.all()
    serializer_class = RecurringModelSerializer
    filter_backends = [RQLFilterBackend]
    rql_filter_class = RecurringFilterClass



