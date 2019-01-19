from rest_framework import serializers

from ..models import UserID
from ..models import Fans


class FansSerializer(serializers.ModelSerializer):

    class Meta:
        model = Fans
        fields = '__all__'

        # read_only_fields = [ ]


class UserIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserID
        fields = '__all__'
