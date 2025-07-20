from datetime import datetime

from dateutil.relativedelta import relativedelta
from dj_rql.drf import RQLFilterBackend
from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from django.utils.dateparse import parse_date
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
    

    @action(detail=False, methods=['get'], url_path='top-descriptions')
    def top_descriptions(self, request):
        user = request.user

        result = (
            Transaction.objects.filter(user=user)
            .values(
                'category__id',
                'category__name',
                'description__id',
                'description__name',
            )
            .annotate(total=Count('id'))
            .order_by('-total')[:10]
        )

        return Response(result)
    
    
    @action(detail=False, methods=['post'], url_path='recurring')
    def create_recurring(self, request):
        data = request.data.copy()
        repeat = int(data.pop('repeat', 0))
        initial_date = data.get('date')

        if not initial_date:
            return Response({'date': 'Campo obrigatório.'}, status=400)

        if repeat == 0:
            repeat = 1200

        try:
            date_obj = datetime.strptime(initial_date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {'date': 'Formato de data inválido. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        instances = []
        for i in range(repeat):
            instance_date = date_obj + relativedelta(months=i)
            instance = Transaction(
                user=request.user,
                description=validated_data.get('description'),
                amount=validated_data.get('amount'),
                category=validated_data.get('category'),
                obs=validated_data.get('obs'),
                date=instance_date,
            )
            instances.append(instance)

        Transaction.objects.bulk_create(instances)

        return Response({'detail': f'{repeat} lançamentos criados.'}, status=status.HTTP_201_CREATED)
    

    @action(detail=False, methods=['delete'], url_path='delete-from-date')
    def delete_from_date(self, request):
        from_date_str = request.data.get("from_date")
        original_id = request.data.get("original_id")

        if not from_date_str or not original_id:
            raise ValidationError({
                "from_date": "Campo obrigatório.",
                "original_id": "Campo obrigatório."
            })

        from_date = parse_date(from_date_str)
        if not from_date:
            raise ValidationError({"from_date": "Data inválida. Use o formato YYYY-MM-DD."})

        try:
            original = Transaction.objects.get(id=original_id, user=request.user)
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transação original não encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        to_delete = Transaction.objects.filter(
            user=request.user,
            description=original.description,
            amount=original.amount,
            date__gte=from_date
        )

        count, _ = to_delete.delete()

        return Response(
            {"message": f"{count} transações deletadas."},
            status=status.HTTP_200_OK
        )
