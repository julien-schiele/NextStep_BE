from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User
from apps.users.factories import UserFactory


class UsersAPITestCase(APITestCase):

    def setUp(self):
        # Create standard user for tests
        self.user = UserFactory(password="password123")
        # Create admin user to test admin views
        self.admin = UserFactory(
            is_staff=True, is_superuser=True, password="password123"
        )

    # ------------------
    # Auth tests
    # ------------------
    def test_login(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url, {"email": self.user.email, "password": "password123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotIn("refresh", response.data)
        self.access_token = response.data["access"]
        self.refresh_token = response.cookies.get("refresh_token")

    def test_refresh_token(self):
        url_login = reverse("token_obtain_pair")

        # LOGIN
        resp_login = self.client.post(
            url_login, {"email": self.user.email, "password": "password123"}
        )

        self.assertEqual(resp_login.status_code, status.HTTP_200_OK)

        refresh_cookie = resp_login.cookies.get("refresh_token")
        self.assertIsNotNone(
            refresh_cookie, "Le cookie refresh_token doit être présent pour le web"
        )

        self.assertIn("access", resp_login.data)
        access_token = resp_login.data["access"]
        self.assertTrue(isinstance(access_token, str) and len(access_token) > 0)

        url_refresh = reverse("token_refresh")
        resp_refresh = self.client.post(url_refresh)
        self.assertEqual(resp_refresh.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp_refresh.data)

    # ------------------
    # Current user tests
    # ------------------
    def test_current_user_authenticated(self):
        # Login to get access token
        url_login = reverse("token_obtain_pair")
        resp_login = self.client.post(
            url_login, {"email": self.user.email, "password": "password123"}
        )
        token = resp_login.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url_me = reverse("current-user")
        resp_me = self.client.get(url_me)
        self.assertEqual(resp_me.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_me.data["email"], self.user.email)

    def test_current_user_unauthenticated(self):
        url_me = reverse("current-user")
        resp_me = self.client.get(url_me)
        self.assertEqual(resp_me.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------
    # User creation
    # ------------------
    def test_create_user_via_api(self):
        url_create = reverse("user-create")
        new_email = UserFactory.build().email
        data = {
            "email": new_email,
            "password": "password123",
            "gdpr_consent": True,
        }
        resp_create = self.client.post(url_create, data)
        self.assertEqual(resp_create.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=new_email).exists())

    # ------------------
    # Admin-only views tests
    # Note: user-list and user-details have been disabled globally
    # ------------------
    # def test_user_list_and_detail_as_non_admin(self):
    #     # Login to get access token
    #     url_login = reverse("token_obtain_pair")
    #     resp_login = self.client.post(
    #         url_login, {"email": self.user.email, "password": "password123"}
    #     )
    #     token = resp_login.data["access"]

    #     self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    #     # Normal user → 403
    #     url_list = reverse("user-list")
    #     resp_list = self.client.get(url_list)
    #     self.assertEqual(resp_list.status_code, status.HTTP_403_FORBIDDEN)

    #     new_user = UserFactory()
    #     url_detail = reverse("user-detail", args=[new_user.id])
    #     resp_detail = self.client.get(url_detail)
    #     self.assertEqual(resp_detail.status_code, status.HTTP_403_FORBIDDEN)

    # def test_user_list_and_detail_as_admin(self):
    #     # Login as admin
    #     url_login = reverse("token_obtain_pair")
    #     resp_login = self.client.post(
    #         url_login, {"email": self.admin.email, "password": "password123"}
    #     )
    #     token = resp_login.data["access"]
    #     self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    #     # User list → should pass
    #     url_list = reverse("user-list")
    #     resp_list = self.client.get(url_list)
    #     self.assertEqual(resp_list.status_code, status.HTTP_200_OK)
    #     self.assertTrue(len(resp_list.data) >= 2)  # admin + user(s)

    #     # User details → should pass
    #     new_user = UserFactory()
    #     url_detail = reverse("user-detail", args=[new_user.id])
    #     resp_detail = self.client.get(url_detail)
    #     self.assertEqual(resp_detail.status_code, status.HTTP_200_OK)
    #     self.assertEqual(resp_detail.data["email"], new_user.email)
