from rest_framework import serializers
from transactions.models import (
    Category,
    Description,
    Transaction,
    Recurring
)


class CategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class DescriptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = '__all__'


class TransactionModelSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'


class RecurringModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurring
        fields = '__all__'
