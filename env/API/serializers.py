from .models import API_Test
from rest_framework import serializers

        

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = API_Test
        fields = ('Label', 'Members')