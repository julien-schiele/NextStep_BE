from apps.programs.models import Program
from apps.programs.serializers import ExerciseSerializer, ProgramSerializer
from .factories import ExerciseFactory, ProgramFactory
from apps.users.factories import UserFactory
from django.forms import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


class BaseTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(password="password123")
        self.admin = UserFactory(
            is_staff=True, is_superuser=True, password="password123"
        )
        self.exercise1 = ExerciseFactory(name="Push Ups")
        self.exercise2 = ExerciseFactory(name="Plank", resolution="duration")


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
        program_data = ProgramFactory.build(content=None)
        program_data.content = {
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
        }

        serializer = ProgramSerializer(
            data={
                "focus": "general_fitness",
                "level": "beginner",
                "is_public": True,
                "content": program_data.content,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        program = serializer.save()
        program.set_current_language("en")
        program.name = "A Program"
        program.save()

    def test_invalid_program_content_missing_slug(self):
        data = {
            "focus": "general_fitness",
            "level": "beginner",
            "is_public": True,
            "content": {
                "version": 1,
                "sessions": [{"sequences": [[{"value": 10}]]}],
            },
        }

        serializer = ProgramSerializer(data=data)
        self.assertTrue(
            serializer.is_valid(), serializer.errors
        )
        program = Program(
            focus=data["focus"], level=data["level"], content=data["content"]
        )
        program.set_current_language("en")
        program.name = "Invalid Program"
        with self.assertRaises(ValidationError):
            program.save()


class ProgramModelTests(BaseTestCase):
    def test_program_save_auto_slug(self):
        program = ProgramFactory.build(
            name="test_program",
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
        self.assertIsNotNone(program.slug)
        self.assertIn("test_program", program.slug)

    def test_program_save_missing_version_raises_error(self):
        program = ProgramFactory.build(
            focus="general_fitness", level="beginner", content={}
        )
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
        program = ProgramFactory.build(
            focus="general_fitness", level="beginner", content=content
        )
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
        program_obj = ProgramFactory.build(content=None)
        program_obj.content = {
            "version": 1,
            "sessions": [
                {
                    "sequences": [
                        [{"exercise": self.exercise1.slug, "value": 10}],
                        [{"exercise": self.exercise2.slug, "value": 30}],
                    ]
                }
            ],
        }
        data = {
            "focus": "general_fitness",
            "level": "beginner",
            "is_public": True,
            "content": program_obj.content,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertIn(
            response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        )
