from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Patient
from rest_framework_simplejwt.tokens import RefreshToken

class PhysicianPatientAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup for two physicians and a patient associated with one physician
        cls.physician1 = get_user_model().objects.create_user(
            email='physician1@example.com',
            password='Testpass123',
            first_name='Physician',
            last_name='One'
        )
        cls.physician2 = get_user_model().objects.create_user(
            email='physician2@example.com',
            password='Testpass123',
            first_name='Physician',
            last_name='Two'
        )
        cls.patient1 = Patient.objects.create(
            physician=cls.physician1,  # Correct reference to physician1
            first_name='John',
            last_name='Doe',
            email='patient@example.com',
            dob='2000-01-01'
        )

    def test_physician_signup(self):
        url = reverse('physician-signup')
        data = {'email': 'newphysician@example.com', 'first_name': 'New', 'last_name': 'Doctor', 'password': 'newpass123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_physician_login(self):
        url = reverse('login')
        data = {'email': 'physician@example.com', 'password': 'testpass123'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_patient(self):
        self.client.force_authenticate(user=self.physician)
        url = reverse('physician-patient-list')
        data = {'first_name': 'Jane', 'last_name': 'Doe', 'email': 'janedoe@example.com', 'dob': '1995-05-05'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_patient(self):
        self.client.force_authenticate(user=self.physician)
        url = reverse('patient-detail', args=[self.patient.id])
        data = {'first_name': 'John', 'last_name': 'Smith'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.last_name, 'Smith')

    def test_delete_patient(self):
        self.client.force_authenticate(user=self.physician)
        url = reverse('patient-detail', args=[self.patient.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Patient.DoesNotExist):
            Patient.objects.get(id=self.patient.id)
    def test_physician_signup_missing_fields(self):
        url = reverse('physician-signup')
        data = {'email': 'incomplete@example.com'}  # Missing name and password
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_wrong_password(self):
        url = reverse('login')
        data = {'email': 'physician@example.com', 'password': 'wrongpass'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_route_unauthenticated(self):
        url = reverse('physician-patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_duplicate_email(self):
        self.client.force_authenticate(user=self.physician)
        url = reverse('physician-patient-list')
        data = {'first_name': 'Duplicate', 'last_name': 'Email', 'email': 'patient@example.com', 'dob': '2001-01-01'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_patient_invalid_data(self):
        self.client.force_authenticate(user=self.physician)
        url = reverse('patient-detail', args=[self.patient.id])
        data = {'dob': '3000-01-01'}  # Future date
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_list_patients_for_physician(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_tokens_for_user(self.physician1)}')
        url = reverse('physician-patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming this physician has only one patient
        self.assertEqual(response.data[0]['email'], 'johndoe@example.com')

    def test_retrieve_patient_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_tokens_for_user(self.physician1)}')
        url = reverse('patient-detail', args=[self.patient1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'johndoe@example.com')

    def test_update_patient_unauthorized_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_tokens_for_user(self.physician2)}')
        url = reverse('patient-detail', args=[self.patient1.id])
        data = {'first_name': 'Johnny'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_patient_unauthorized_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_tokens_for_user(self.physician2)}')
        url = reverse('patient-detail', args=[self.patient1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
