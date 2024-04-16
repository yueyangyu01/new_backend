from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Patient, Physician, SecurePatientRecord
from .serializers import PatientSerializer, PhysicianSerializer
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .permissions import IsOwnerOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice
from channels.generic.websocket import AsyncWebsocketConsumer
import json

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({'message': message}))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_patient_info(request, patient_id):
    if not request.user.is_authenticated or not hasattr(request.user, 'doctor'):
        return JsonResponse({"error": "Unauthorized access"}, status=403)

    try:
        patient = Patient.objects.get(id=patient_id, doctor=request.user.doctor)
        send_mail(
            'Your Patient Information',
            'Please visit this link to view your information: http://localhost:3000/patient-info',
            'your_email@example.com',
            [patient.email],
            fail_silently=False,
        )
        return JsonResponse({"status": "Email sent successfully"})
    except Patient.DoesNotExist:
        return JsonResponse({"error": "Patient not found"}, status=404)

# Physician SignUp View
class PhysicianSignUpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PhysicianSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(user.password)
            user.save()
            logger.info(f"New physician signed up: {user.email}")
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Physician signup validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Encryption at Rest for Patient Records
class SecurePatientDetailView(generics.RetrieveAPIView):
    queryset = SecurePatientRecord.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        patient_id = self.kwargs.get('pk')
        return SecurePatientRecord.objects.get(id=patient_id)

# Two-Factor Authentication
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_two_factor(request, token):
    user = request.user
    device = TOTPDevice.objects.filter(user=user).first()
    if device.verify_token(token):
        return Response({"message": "2FA verified"})
    else:
        return Response({"error": "Invalid 2FA token"}, status=status.HTTP_400_BAD_REQUEST)

# Real-time notifications
class PatientRealtimeUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Example implementation that needs real-time handling
        patient_data = request.data
        patient = Patient.objects.get(id=patient_data['id'])
        patient.diagnosis = patient_data['diagnosis']
        patient.save()
        # Notify all subscribed clients
        NotificationConsumer.send(json.dumps({
            'type': 'update',
            'message': f'Patient {patient.id} updated'
        }))
        return Response({"message": "Patient updated and notifications sent"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_patient_info(request, patient_id):
    if not request.user.is_authenticated or not hasattr(request.user, 'doctor'):
        return JsonResponse({"error": "Unauthorized access"}, status=403)

    try:
        patient = Patient.objects.get(id=patient_id, doctor=request.user.doctor)
        send_mail(
            'Your Patient Information',
            'Please visit this link to view your information: http://localhost:3000/patient-info',
            'your_email@example.com',  # Your sender email
            [patient.email],  # Recipient email
            fail_silently=False,
        )
        return JsonResponse({"status": "Email sent successfully"})
    except Patient.DoesNotExist:
        return JsonResponse({"error": "Patient not found"}, status=404)


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
