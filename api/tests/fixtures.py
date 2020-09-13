import pytest
from django.contrib.auth.models import User
from api.models import Course, ClassRoom, Phase

@pytest.fixture
def authorized_user(db):
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def course(db):
    phase = Phase(title='Lobby')
    phase.save()
    phase2 = Phase(title='calculate', timer=True)
    phase2.save()
    course = Course(title='Math', default_phase=phase)
    course.save()
    course.phases.add(phase)
    course.phases.add(phase2)
    course.save()
    return course

@pytest.fixture
def class_room(db, course):
  class_room = ClassRoom(course=course)
  class_room.save()
  return class_room


@pytest.fixture
def phase(db):
    phase = Phase(title='some new phase')
    phase.save()
    return phase
