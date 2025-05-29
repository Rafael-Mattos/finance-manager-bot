from rest_framework import viewsets
from transactions.models import *
from transactions.serializers import *

class GroupModelViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupModelSerializer


class DescriptionModelViewSet(viewsets.ModelViewSet):
    queryset = Description.objects.all()
    serializer_class = DescriptionModelSerializer


class TransactionModelViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionModelSerializer


class RecurringModelViewSet(viewsets.ModelViewSet):
    queryset = Recurring.objects.all()
    serializer_class = RecurringModelSerializer



