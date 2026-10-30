from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from BrightPath.models import Profile

# Python 3.14 compatibility monkeypatch for Django Template Context copy
import copy
from django.template.context import BaseContext

def patch_base_context_copy(self):
    duplicate = self.__class__.__new__(self.__class__)
    duplicate.dicts = self.dicts[:]
    for k, v in self.__dict__.items():
        if k != 'dicts':
            try:
                setattr(duplicate, k, copy.copy(v))
            except Exception:
                setattr(duplicate, k, v)
    return duplicate

BaseContext.__copy__ = patch_base_context_copy

class BrightPathAuthTestCase(TestCase):
    def setUp(self):
        # Create test users with usernames equal to their email addresses
        self.superadmin = User.objects.create_superuser(
            username='superadmin_test@example.com',
            email='superadmin_test@example.com',
            password='password123',
            first_name='Super Admin'
        )
        self.admin = User.objects.create_superuser(
            username='admin_test@example.com',
            email='admin_test@example.com',
            password='password123',
            first_name='Admin'
        )
        self.staff = User.objects.create_user(
            username='staff_test@example.com',
            email='staff_test@example.com',
            password='password123',
            is_staff=True,
            first_name='Staff'
        )
        self.student = User.objects.create_user(
            username='student_test@example.com',
            email='student_test@example.com',
            password='password123',
            first_name='Student'
        )

    def test_profile_automatic_creation(self):
        # Verify that profiles are automatically created by signals
        self.assertTrue(Profile.objects.filter(user=self.superadmin).exists())
        self.assertTrue(Profile.objects.filter(user=self.admin).exists())
        self.assertTrue(Profile.objects.filter(user=self.staff).exists())
        self.assertTrue(Profile.objects.filter(user=self.student).exists())

    def test_signup_integrity(self):
        # Test signup via POST request to verify no duplicates / IntegrityError occurs
        client = Client()
        response = client.post(reverse('signup'), {
            'name': 'New Student',
            'number': '1234567890',
            'email': 'newstudent@example.com',
            'address': 'Test Address',
            'bd': '2000-01-01',
            'password': 'password123'
        })
        # Check redirect to student dashboard after successful signup
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('student_dashboard'))
        
        # Verify user and profile exist
        user = User.objects.get(email='newstudent@example.com')
        self.assertEqual(user.first_name, 'New Student')
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.phone, '1234567890')

    def test_role_redirection_on_login(self):
        client = Client()
        
        # Superadmin login redirect
        response = client.post(reverse('login'), {
            'email': 'superadmin_test@example.com',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))
        client.logout()

        # Admin login redirect
        response = client.post(reverse('login'), {
            'email': 'admin_test@example.com',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))
        client.logout()

        # Staff login redirect
        response = client.post(reverse('login'), {
            'email': 'staff_test@example.com',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('staff_dashboard'))
        client.logout()

        # Student login redirect
        response = client.post(reverse('login'), {
            'email': 'student_test@example.com',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_unauthorized_dashboard_access(self):
        client = Client()
        
        # Login as student
        client.login(username='student_test@example.com', password='password123')
        
        # Accessing admin dashboard should raise PermissionDenied (403 status code)
        response = client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)
        
        # Accessing staff dashboard should raise PermissionDenied
        response = client.get(reverse('staff_dashboard'))
        self.assertEqual(response.status_code, 403)
        
        # Accessing student dashboard is allowed (200 status code)
        response = client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        client.logout()
        
        # Login as staff
        client.login(username='staff_test@example.com', password='password123')
        
        # Accessing admin dashboard should raise PermissionDenied
        response = client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)
        
        # Accessing staff dashboard is allowed
        response = client.get(reverse('staff_dashboard'))
        self.assertEqual(response.status_code, 200)
