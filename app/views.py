from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Patient, Physician
from .serializers import PatientSerializer, PhysicianSerializer
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .permissions import IsOwnerOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_physician_info(request):
    """
    Get the currently logged-in physician's information.
    """
    physician = request.user
    return Response({
        'first_name': physician.first_name,
        'last_name': physician.last_name,
    })

# CreateAPIView for Patients: This view is correctly set up to associate the created patient with the logged-in physician.
class PatientCreateView(generics.CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(physician=self.request.user)

# Physician SignUp View: This view handles the registration of new physicians.
class PhysicianSignUpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PhysicianSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(user.password)
            user.save()
            logger.info(f"New physician signed up: {user.email}")

            # Generate tokens for the user
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Physician signup validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View for retrieving, updating, and deleting patient details: This view correctly restricts actions to the owner or through appropriate permissions.
class PatientDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"], physician=self.request.user)

# Login View: This view handles physician login.
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login Successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# Physician's Patient List View: This view lists all patients associated with the logged-in physician and allows for the creation of new patients.
class PhysicianPatientListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patients = Patient.objects.filter(physician=request.user)
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PatientSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(physician=request.user)
            logger.info(f"New patient created by {request.user.email}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Patient creation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
