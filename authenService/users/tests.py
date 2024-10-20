from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from users.models import User


class EmployeeListViewTest(APITestCase):

    def setUp(self):
        # Create a customer and an employee users
        self.customer = User.objects.create(
            username='customer',
            password='customerpassword',
            first_name='Cus',
            last_name='Tomer',
            user_type=User.CUSTOMER
        )
        self.employee = User.objects.create(
            username='employee',
            password='employeepassword',
            first_name='Emp',
            last_name='Loyee',
            user_type=User.EMPLOYEE)
        
        self.url = reverse('users-list-employee')

    def test_list_employees(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'Emp')


class PatchEmployeeRatingViewTest(APITestCase):

    def setUp(self):
        # Create a customer and an employee users
        self.customer = User.objects.create(
            username='customer',
            password='customerpassword',
            first_name='Cus',
            last_name='Tomer',
            user_type=User.CUSTOMER
        )
        self.employee = User.objects.create(
            username='employee',
            password='employeepassword',
            first_name='Emp',
            last_name='Loyee',
            user_type=User.EMPLOYEE)
        
        self.url = reverse('users-patch-rating')

    def test_patch_employee_rating_success(self):
        response = self.client.patch(f'{self.url}?user_id={self.employee.id}&new_rating=4.5')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.rating, 4.5)

    def test_patch_employee_rating_missing_params(self):
        response = self.client.patch(f'{self.url}?user_id={self.employee.id}')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Both user_id and new_rating are required.', response.data['detail'])

    def test_patch_employee_rating_invalid_rating(self):
        response = self.client.patch(f'{self.url}?user_id={self.employee.id}&new_rating=aaa')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Rating must be a valid number.', response.data['detail'])

    def test_patch_employee_rating_out_of_range(self):
        response = self.client.patch(f'{self.url}?user_id={self.employee.id}&new_rating=-1.0')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Rating must be between 0 and 5.', response.data['detail'])

    def test_patch_employee_rating_user_not_found(self):
        response = self.client.patch(f'{self.url}?user_id=999&new_rating=4.5')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User not found.', response.data['detail'])

    def test_patch_employee_rating_invalid_user_type(self):
        response = self.client.patch(f'{self.url}?user_id={self.customer.id}&new_rating=4.5')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('This is invalid transaction.', response.data['detail'])