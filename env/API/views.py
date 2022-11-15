from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import API_Test
from .serializers import GroupSerializer
# Create your views here.

class GroupList(APIView):

	def get(self, request):
		groups = API_Test.objects.all()
		serializer = GroupSerializer(groups, many=True)
		return Response(serializer.data)
