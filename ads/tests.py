from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from .models import Ad

User = get_user_model()  # 🔥 Uses the correct user model


class AdModelTest(TestCase):
    """Tests for the Ad model"""

    def test_create_ad(self):
        """Ensure an ad can be created successfully"""
        ad = Ad.objects.create(
            title="50% Off Sale!",
            image="https://via.placeholder.com/150",
            link="https://www.sale.com",
            weight=3,
            is_active=True,
        )

        self.assertEqual(Ad.objects.count(), 1)
        self.assertEqual(ad.title, "50% Off Sale!")
        self.assertEqual(ad.weight, 3)
        self.assertTrue(ad.is_active)


class AdViewTest(TestCase):
    """Tests for Ad API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.admin_client = APIClient()  # 🔥 Separate client for admin actions

        # Create users
        self.user = User.objects.create_user(
            email="user@example.com", password="testpass"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="testpass"
        )

        # Create an admin group and add the admin user to it
        self.admin_group = Group.objects.create(name="admin")
        self.admin_user.groups.add(self.admin_group)

        # 🔥 Authenticate users using force_authenticate
        self.client.force_authenticate(user=self.user)
        self.admin_client.force_authenticate(user=self.admin_user)

        # Create test ads
        self.ad1 = Ad.objects.create(
            title="Ad One",
            image="https://via.placeholder.com/150",
            link="https://example.com",
            weight=2,
            is_active=True,
        )
        self.ad2 = Ad.objects.create(
            title="Ad Two",
            image="https://via.placeholder.com/150",
            link="https://example.com",
            weight=4,
            is_active=False,
        )

    def test_list_ads(self):
        """Ensure ads can be retrieved via GET request"""
        response = self.client.get("/api/ads/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_view_ads(self):
        """Ensure admin can see all ads in the admin view"""
        response = self.admin_client.get("/api/ads/admin-view/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_ad_as_admin(self):
        """Ensure an admin user can create an ad"""
        data = {
            "title": "New Ad",
            "image": "https://via.placeholder.com/150",
            "link": "https://newad.com",
            "weight": 5,
            "is_active": True,
        }
        response = self.admin_client.post(
            "/api/ads/", data, format="json"
        )  # 🔥 Uses admin client
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ad.objects.count(), 3)

    def test_create_ad_as_non_admin(self):
        """Ensure non-admin users cannot create an ad"""
        data = {
            "title": "New Ad",
            "image": "https://via.placeholder.com/150",
            "link": "https://newad.com",
            "weight": 5,
            "is_active": True,
        }
        response = self.client.post(
            "/api/ads/", data, format="json"
        )  # 🔥 Uses regular user client
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Ad.objects.count(), 2)

    def test_update_ad_as_admin(self):
        """Ensure an admin user can update an ad"""
        data = {"title": "Updated Ad", "weight": 10}
        response = self.admin_client.patch(
            f"/api/ads/{self.ad1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.title, "Updated Ad")
        self.assertEqual(self.ad1.weight, 10)

    def test_update_ad_as_non_admin(self):
        """Ensure non-admin users cannot update an ad"""
        data = {"title": "Hacked Ad"}
        response = self.client.patch(f"/api/ads/{self.ad1.id}/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_ad_as_admin(self):
        """Ensure an admin user can delete an ad"""
        response = self.admin_client.delete(f"/api/ads/{self.ad1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ad.objects.count(), 1)

    def test_delete_ad_as_non_admin(self):
        """Ensure non-admin users cannot delete an ad"""
        response = self.client.delete(f"/api/ads/{self.ad1.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Ad.objects.count(), 2)
