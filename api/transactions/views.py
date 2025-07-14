from datetime import datetime

from dateutil.relativedelta import relativedelta
from dj_rql.drf import RQLFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from transactions.filters import (
    CategoryFilterClass,
    DescriptionFilterClass,
    TransactionFilterClass
)
from transactions.models import (
    Category,
    Description,
    Transaction
)
from transactions.serializers import (
    CategoryModelSerializer,
    DescriptionModelSerializer,
    DescriptionListModelSerializer,
    TransactionModelSerializer,
    TransactionListModelSerializer
)


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

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return DescriptionListModelSerializer

        return DescriptionModelSerializer


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

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TransactionListModelSerializer

        return TransactionModelSerializer
    
    @action(detail=False, methods=['post'], url_path='recurring')
    def create_recurring(self, request):
        data = request.data.copy()
        repeat = int(data.pop('repeat', 1))
        initial_date = data.get('date')

        if not initial_date:
            return Response({'date': 'Campo obrigatório.'}, status=400)

        try:
            date_obj = datetime.strptime(initial_date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {
                    'date': 'Formato de data inválido. Use YYYY-MM-DD.'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        created = []

        for i in range(repeat):
            instance_data = data.copy()
            instance_data['date'] = (date_obj + relativedelta(months=+i)).isoformat()

            serializer = self.get_serializer(data=instance_data)
            serializer.is_valid(raise_exception=True)

            description = serializer.validated_data.get('description')
            category = description.category
            serializer.save(user=request.user, category=category)

            created.append(serializer.data)

        return Response(created, status=status.HTTP_201_CREATED)
