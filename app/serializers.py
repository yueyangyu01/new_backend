from rest_framework import serializers
from .models import Patient, Physician

class PhysicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Physician
        fields = ('id', 'first_name', 'last_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'first_name', 'last_name', 'email', 'dob', 'mri_file')  # Removed 'physician'

    def create(self, validated_data):
        # Assuming 'request' is passed to the serializer's context in the view
        request = self.context.get('request')
        validated_data['physician'] = request.user
        return super().create(validated_data)
