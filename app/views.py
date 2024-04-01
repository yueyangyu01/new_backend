from django.shortcuts import render
from rest_framework.views import APIView
from . models import *
from . serializers import *
from rest_framework.response import Response

class PatientView(APIView):
	def get(self, request):
		output = [{"first_name": output.first_name, "last_name": output.last_name, "email": output.email, "dob": output.dob, "mri_file": output.mri_file} 
			for output in Patient.objects.all()]
		return Response(output)
		
	def post(self, request):
		serializer = PatientSerializer(data=request.data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response(serializer.data, status=201)