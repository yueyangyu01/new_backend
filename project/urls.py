from django.contrib import admin
from django.urls import path
from app.views import (
    PhysicianSignUpView,
    LoginView,
    PhysicianPatientListView,
    PatientDetailUpdateDeleteView,
    PatientCreateView,
    get_physician_info,  # Import the new view function
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', PhysicianSignUpView.as_view(), name='physician-signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('physician/info/', get_physician_info, name='physician-info'),  # New endpoint to fetch physician info
    path('patients/', PhysicianPatientListView.as_view(), name='physician-patient-list'),
    path('patients/create/', PatientCreateView.as_view(), name='patient-create'),  
    path('patients/<int:pk>/', PatientDetailUpdateDeleteView.as_view(), name='patient-detail'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]