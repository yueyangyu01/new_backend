# new_backend

Run these commands before running server

Pip install pipenv
Pipenv install djangorestframework
Pipenv install django-cors-headers

Create and activate virtual environment
virtualenv newenv
source newenv/bin/activate

Install Django:
pip install django

Database tables
Python manage.py make-migrations
Python manage.py migrate
Python manage.py createsuperuser

Run server:
Python manage.py runserver

NeuroMap Backend Repository
Overview
This repository contains the backend for NeuroMap, a Django-based application designed to enhance brain tumor visualization and facilitate physician-patient communication. This platform leverages advanced Django features, JWT authentication, and robust security practices to manage sensitive medical data.

Key Features
Secure Patient Record Management: Handles patient data securely with the SecurePatientRecord model, ensuring data integrity and security.
JWT Authentication: Utilizes JSON Web Tokens for secure user session management, enhancing security across physician and patient interactions.
Email Notifications: Implements an email system to communicate patient information securely, ensuring patient engagement and data privacy.
API Development: Features RESTful API endpoints for patient and physician data management, crafted with Django's robust framework for efficient data handling.
Advanced Logging: Integrates detailed logging mechanisms to aid in debugging and maintaining the application, ensuring reliability and performance.
Installation
Clone the repository:
bash
Copy code
git clone [repository-url]
Install required packages:
Copy code
pip install -r requirements.txt
Initialize the database:
Copy code
python manage.py migrate
Run the server:
Copy code
python manage.py runserver
Usage
Ensure you are logged in as a physician to access patient records. Use provided API endpoints to manage patient records, sign up as a physician, or log in to the system.

Security
This application uses Django's security best practices, including hashed passwords, token authentication, and HTTPS for data transmission to protect against common vulnerabilities.

Contributing
Contributions are welcome! Please fork the repository and submit pull requests with your proposed changes. For major changes, please open an issue first to discuss what you would like to change.

