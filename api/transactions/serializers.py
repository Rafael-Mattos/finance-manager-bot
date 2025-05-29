from rest_framework import serializers
from transactions.models import *

class GroupModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class DescriptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = '__all__'


class TransactionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class RecurringModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurring
        fields = '__all__'

