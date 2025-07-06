from rest_framework import serializers
from transactions.models import (
    Category,
    Description,
    Transaction
)


class CategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class DescriptionListModelSerializer(serializers.ModelSerializer):
    category = CategoryModelSerializer(read_only=True)
    
    class Meta:
        model = Description
        fields = '__all__'


class DescriptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = '__all__'


class TransactionListModelSerializer(serializers.ModelSerializer):
    category = CategoryModelSerializer(read_only=True)
    description = DescriptionModelSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionModelSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
