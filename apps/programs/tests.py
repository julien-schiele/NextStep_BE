from apps.users.factories import UserFactory
from django.forms import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from .models import Program, Exercise
from .serializers import ProgramSerializer, ExerciseSerializer


class BaseTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(password="password123")
        self.admin = UserFactory(
            is_staff=True, is_superuser=True, password="password123"
        )

        self.exercise1 = Exercise.objects.create()
        self.exercise1.set_current_language("en")
        self.exercise1.name = "Push Ups"
        self.exercise1.save()

        self.exercise2 = Exercise.objects.create()
        self.exercise2.set_current_language("en")
        self.exercise2.name = "Plank"
        self.exercise2.resolution = "duration"
        self.exercise2.save()


class ExerciseSerializerTests(BaseTestCase):
    def test_valid_resolution(self):
        data = {
            "translations": {
                "en": {"name": "myExercise", "description": "someDescriptiveContent"}
            },
            "practice_zone": "everywhere",
            "resolution": "repetition",
        }
        serializer = ExerciseSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_resolution(self):
        data = {
            "practice_zone": "everywhere",
            "resolution": "invalid_value",
        }
        serializer = ExerciseSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("resolution", serializer.errors)


class ProgramSerializerTests(BaseTestCase):
    def test_valid_program_content(self):
        data = {
            "focus": "general_fitness",
            "level": "beginner",
            "duration_days": 7,
            "is_public": True,
            "content": {
                "version": 1,
                "sessions": [
                    {
                        "sequences": [
                            [
                                {
                                    "exercise": self.exercise1.slug,
                                    "value": 10,
                                    "practice_zone": "everywhere",
                                },
                                {
                                    "exercise": self.exercise2.slug,
                                    "value": 30,
                                    "practice_zone": "everywhere",
                                },
                            ]
                        ]
                    }
                ],
            },
        }

        serializer = ProgramSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Save and set translation manually
        program = serializer.save()
        program.set_current_language("en")
        program.name = "A Program"
        program.save()

    def test_invalid_program_content_missing_slug(self):
        data = {
            "focus": "general_fitness",
            "level": "beginner",
            "duration_days": 7,
            "is_public": True,
            "content": {
                "version": 1,
                "sessions": [{"sequences": [[{"value": 10}]]}],
            }
        }

        serializer = ProgramSerializer(data=data)
        self.assertTrue(
            serializer.is_valid(), serializer.errors
        )  # Serializer passes because content validation is model-level

        # Save should raise ValidationError
        program = Program(
            focus=data["focus"], level=data["level"], content=data["content"]
        )
        program.set_current_language("en")
        program.name = "Invalid Program"
        with self.assertRaises(ValidationError):
            program.save()


class ProgramModelTests(BaseTestCase):
    def test_program_save_auto_slug(self):
        program = Program(
            focus="general_fitness",
            level="beginner",
            content={
                "version": 1,
                "sessions": [
                    {
                        "sequences": [
                            [{"exercise": self.exercise1.slug, "value": 10}],
                            [{"exercise": self.exercise2.slug, "value": 30}],
                        ]
                    }
                ],
            },
        )
        program.set_current_language("en")
        program.name = "Test Program"
        program.save()
        self.assertEqual(program.slug, "test_program")

    def test_program_save_missing_version_raises_error(self):
        program = Program(focus="general_fitness", level="beginner", content={})
        program.set_current_language("en")
        program.name = "Invalid Program"

        with self.assertRaises(ValidationError):
            program.save()

    def test_program_duration_calculation(self):
        content = {
            "version": 1,
            "sessions": [
                {
                    "sequences": [
                        [{"exercise": self.exercise1.slug, "value": 10}],
                        [{"exercise": self.exercise2.slug, "value": 30}],
                    ]
                }
            ],
            "repeat": {"cycles": 3},
        }
        program = Program(focus="general_fitness", level="beginner", content=content)
        program.set_current_language("en")
        program.name = "Duration Test"
        program.save()
        self.assertEqual(program.duration_days, 1 * 3)  # 1 session * 3 cycles


class ProgramViewSetPermissionsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.url = reverse("program-list")

    def test_get_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin)
        data = {
            "focus": "general_fitness",
            "level": "beginner",
            "content": {
                "version": 1,
                "sessions": [
                    {
                        "sequences": [
                            [{"exercise": self.exercise1.slug, "value": 10}],
                            [{"exercise": self.exercise2.slug, "value": 30}],
                        ]
                    }
                ],
            },
        }
        response = self.client.post(self.url, data, format="json")
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        )
