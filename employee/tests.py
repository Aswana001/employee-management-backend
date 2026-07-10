from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from employee.models import Department, Designation, Employee

class EmployeeManagementAPITests(APITestCase):
    
    def setUp(self):
        # Create prerequisite master lookup values
        self.department = Department.objects.create(name="Engineering", description="Core tech devs")
        self.designation = Designation.objects.create(title="Software Engineer II", description="L2 Dev")
        
        self.employee_payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@company.com",
            "phone": "+1234567890",
            "address": "123 Innovation Way, Tech City",
            "date_of_birth": "1995-05-15",
            "gender": "F",
            "salary": "95000.00",
            "joining_date": "2024-01-10",
            "department": self.department.id,
            "designation": self.designation.id
        }

    def test_create_employee_success(self):
        """Validates that a correctly formatted payload results in employee generation."""
        url = reverse('employee-list')
        response = self.client.post(url, self.employee_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['employee_code'], "EMP0001") # Automated custom numbering test

    def test_joining_date_validation_failure(self):
        """Ensures that cross-field logical rules trigger validation failure errors cleanly."""
        # Mutate payload to make joining date occur BEFORE birthday
        self.employee_payload["joining_date"] = "1990-01-01"
        url = reverse('employee-list')
        
        response = self.client.post(url, self.employee_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("joining_date", response.data)