# apps/programs/tests/factories.py
import uuid
import factory
from faker import Faker
from django.utils.text import slugify
from apps.programs.models import Exercise, Program
from apps.programs.choices import Resolution, PracticeZone, Focus, Level

fake = Faker()


class ExerciseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Exercise

    resolution = factory.Iterator([Resolution.REPETITION, Resolution.DURATION])
    practice_zone = factory.Iterator(
        [PracticeZone.EVERYWHERE, PracticeZone.CLIMBING_GYM]
    )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = super()._create(model_class, *args, **kwargs)
        obj.set_current_language("en")
        obj.name = f"{fake.word().capitalize()}_{uuid.uuid4().hex[:6]}"
        obj.description = fake.sentence(nb_words=10)
        obj.slug = slugify(obj.name).replace("-", "_")
        obj.save()
        return obj


class ProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Program

    focus = factory.Iterator([Focus.GENERAL_FITNESS, Focus.CLIMBING_PERFORMANCE])
    level = factory.Iterator([Level.BEGINNER, Level.INTERMEDIATE, Level.ADVANCED])
    is_public = True

    @factory.lazy_attribute
    def content(self):
        ex1 = ExerciseFactory()
        ex2 = ExerciseFactory()
        return {
            "version": 1,
            "sessions": [
                {
                    "session": 1,
                    "focus": Focus.CLIMBING_PERFORMANCE,
                    "sequences": [
                        [
                            {
                                "exercise": ex1.slug,
                                "value": fake.random_int(5, 20),
                                "practice_zone": PracticeZone.EVERYWHERE,
                            },
                            {
                                "exercise": ex2.slug,
                                "value": fake.random_int(10, 60),
                                "practice_zone": PracticeZone.CLIMBING_GYM,
                            },
                        ]
                    ],
                }
            ],
            "repeat": {"cycles": fake.random_int(1, 3)},
        }

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        obj = super()._create(model_class, *args, **kwargs)
        obj.set_current_language("en")
        obj.name = f"{fake.word().capitalize()}_{uuid.uuid4().hex[:6]}"
        obj.slug = slugify(obj.name).replace("-", "_")
        obj.save()
        return obj
