from dj_rql.drf import RQLFilterBackend
from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from transactions.filters import (CategoryFilterClass, 
                                  DescriptionFilterClass, 
                                  TransactionFilterClass, 
                                  RecurringFilterClass
                                  )
from transactions.models import *
from transactions.serializers import *

class CategoryModelViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryModelSerializer
    filter_backends = [RQLFilterBackend]
    rql_filter_class = CategoryFilterClass


class DescriptionModelViewSet(viewsets.ModelViewSet):
    queryset = Description.objects.all()
    serializer_class = DescriptionModelSerializer
    filter_backends = [RQLFilterBackend]
    rql_filter_class = DescriptionFilterClass
    # permission_classes = [permissions.DjangoModelPermissions]


class TransactionModelViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionModelSerializer
    filter_backends = [RQLFilterBackend]
    rql_filter_class = TransactionFilterClass

    def perform_create(self, serializer):
        description = serializer.validated_data.get('description')

        if not description:
            raise ValidationError({'description': 'Descrição é obrigatória.'})

        category = description.category
        serializer.save(user=self.request.user, category=category)
        print(serializer)
    
    def perform_update(self, serializer):
        description = serializer.validated_data.get('description')

        if description:
            category = description.category
            serializer.save(category=category)
        else:
            serializer.save()


class RecurringModelViewSet(viewsets.ModelViewSet):
    queryset = Recurring.objects.all()
    serializer_class = RecurringModelSerializer
    filter_backends = [RQLFilterBackend]
    rql_filter_class = RecurringFilterClass



