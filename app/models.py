from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class SecurePatientRecord(models.Model):
    # Linking to the Physician model
    physician = models.ForeignKey('Physician', related_name='patient_records', on_delete=models.CASCADE)
    
    # Additional fields for patient records
    record_date = models.DateField(auto_now_add=True)  # Automatically sets the date when record is created
    description = models.TextField(blank=True, null=True)  # Optional field for record details
    file_path = models.FileField(upload_to='patient_records/')  # Store files related to the patient records

    def __str__(self):
        # Return a string representation that could include the date and description
        return f"{self.record_date} - {self.description[:50]}"  # Show only the first 50 characters
class PhysicianManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, password=password, first_name=first_name, last_name=last_name)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Physician(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Use is_staff instead of is_admin

    objects = PhysicianManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

class Patient(models.Model):
    physician = models.ForeignKey(Physician, related_name='patients', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    dob = models.DateField()
    mri_file = models.FileField(upload_to='mri_files/', null=True, blank=True)
