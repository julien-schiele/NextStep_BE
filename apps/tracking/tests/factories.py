# apps/tracking/tests/factories.py
import uuid
from apps.programs.models import Program
import factory
from faker import Faker
from apps.tracking.models import (
    UserProgram,
    UserProgramSession,
    UserProgramFeedback,
)

fake = Faker()


class UserProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProgram

    id = factory.LazyFunction(uuid.uuid4)
    user = factory.SubFactory("apps.users.factories.UserFactory")
    program = factory.SubFactory("apps.programs.tests.factories.ProgramFactory")
    status = "active"


class UserProgramSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProgramSession

    id = factory.LazyFunction(uuid.uuid4)
    user_program = factory.SubFactory(UserProgramFactory)
    session_in_cycle = factory.LazyFunction(lambda: fake.random_int(1, 10))
    cycle_count = 1
    rating = "ok"
    session_snapshot = ({"dummy": "data"},)


class UserProgramFeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProgramFeedback

    id = factory.LazyFunction(uuid.uuid4)
    user_program = factory.SubFactory(UserProgramFactory)
    usefulness = "useful"
    would_repeat = True
    comment = factory.LazyFunction(lambda: fake.sentence())
