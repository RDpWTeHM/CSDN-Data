from rest_framework import serializers

from ..models import UserID
from ..models import Fans
from ..models import VisualData


class FansSerializer(serializers.ModelSerializer):

    class Meta:
        model = Fans
        fields = '__all__'

        # read_only_fields = [ ]


class VisualDataSerialzier(serializers.ModelSerializer):
    class Meta:
        model = VisualData
        fields = '__all__'


class UserIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserID
        fields = '__all__'
