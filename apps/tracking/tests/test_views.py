from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from apps.tracking.models import (
    UserProgram,
    UserProgramSession,
    UserProgramFeedback,
)
from .factories import (
    UserProgramFactory,
    UserProgramSessionFactory,
    UserProgramFeedbackFactory,
)

import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "password")


class TrackingAPITests(APITestCase):
    def setUp(self):
        # Users
        self.user1 = UserFactory(email="u1@domain.com", password="pass")
        self.user2 = UserFactory(email="u2@domain.com", password="pass")

        # API clients
        self.client1 = APIClient()
        self.client2 = APIClient()
        self.client1.force_authenticate(user=self.user1)
        self.client2.force_authenticate(user=self.user2)

        # UserPrograms
        self.up1 = UserProgramFactory(user=self.user1)
        self.up1_s1 = UserProgramSessionFactory(user_program=self.up1)
        self.up1_fb = UserProgramFeedbackFactory(user_program=self.up1)

        self.up2 = UserProgramFactory(user=self.user2)
        UserProgramSessionFactory(user_program=self.up2)
        UserProgramFeedbackFactory(user_program=self.up2)

    # --------------------------------------------------
    # UserProgram
    # --------------------------------------------------
    def test_user_can_list_only_own_user_programs(self):
        url = reverse("user-program-list")
        res = self.client1.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)
        self.assertEqual(res.json()[0]["id"], str(self.up1.id))

    def test_user_cannot_see_other_user_program(self):
        url = reverse("user-program-detail", kwargs={"pk": self.up2.id})
        res = self.client1.get(url)
        self.assertEqual(res.status_code, 404)

    def test_user_can_patch_own_user_program(self):
        url = reverse("user-program-detail", kwargs={"pk": self.up1.id})
        res = self.client1.patch(
            url,
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)

        self.up1.refresh_from_db()
        self.assertEqual(self.up1.status, "completed")

    # --------------------------------------------------
    # Sessions
    # --------------------------------------------------
    def test_list_sessions_for_user_program(self):
        url = reverse("user-program-sessions", kwargs={"user_program_id": self.up1.id})
        res = self.client1.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

    def test_cannot_list_sessions_of_other_user(self):
        url = reverse("user-program-sessions", kwargs={"user_program_id": self.up2.id})
        res = self.client1.get(url)
        self.assertEqual(res.status_code, 403)

    def test_create_session_progress(self):
        payload = {
            "user_program": str(self.up1.id),
            "session_in_cycle": 2,
            "cycle_count": 1,
            "session_snapshot": {"dummy": "data"},
        }
        
        url = reverse("user-program-sessions", kwargs={"user_program_id": self.up1.id})
        self.assertEqual(UserProgramSession.objects.filter(user_program=self.up1).count(), 1)
        res = self.client1.post(url, payload, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(UserProgramSession.objects.filter(user_program=self.up1).count(), 2)

    # --------------------------------------------------
    # Feedback
    # --------------------------------------------------
    def test_list_feedback_for_user_program(self):
        url = reverse("user-program-feedbacks", kwargs={"user_program_id": self.up1.id})
        res = self.client1.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

    def test_cannot_see_other_user_feedback(self):
        url = reverse("user-program-feedbacks", kwargs={"user_program_id": self.up2.id})
        res = self.client1.get(url)
        self.assertEqual(res.status_code, 403)

    def test_create_feedback(self):
        payload = {
            "user_program": str(self.up1.id),
            "usefulness": "very_useful",
            "would_repeat": False,
            "comment": "Great program",
        }
        url = reverse("user-program-feedbacks", kwargs={"user_program_id": self.up1.id})
        res = self.client1.post(url, payload, format="json")

        self.assertEqual(res.status_code, 201)
        self.assertEqual(UserProgramFeedback.objects.count(), 3)
