import pytest
from django.db.utils import IntegrityError

from api.constants import (
    EVENT_ACTION_CHANGE_PHASE,
    EVENT_ACTION_JOIN,
    EVENT_ACTION_LEAVE
)
from api.models import ClassRoom, Course, Event, Phase
from api.tests.fixtures import authorized_user, course, class_room

class TestPhase:

    @pytest.mark.django_db
    def test_phase_save_success(self):
        phase = Phase(title='Cool')
        phase.save()
        assert phase.title == 'Cool'
        assert '{}'.format(phase) == 'Cool'
        assert phase.timer == False

    @pytest.mark.django_db
    def test_empty_title_fail(self):
        phase = Phase(title=None)
        with pytest.raises(IntegrityError):
            phase.save()

class TestClassRoom:

    @pytest.mark.django_db
    def test_class_room_kick_off(self, authorized_user, course):

        class_room = ClassRoom.kick_off(course, authorized_user)
        assert 'class room of : Math' == '{}'.format(class_room)

        assert class_room.attending.all().count() == 1
        assert class_room.attending.all().first() == authorized_user

        assert class_room.events.all().count() == 2
        event_1 = class_room.events.all()[0]
        event_2 = class_room.events.all()[1]

        assert event_1.action == EVENT_ACTION_CHANGE_PHASE
        assert event_1.user == authorized_user
        assert event_1.to_phase_id == course.default_phase.id

        assert event_2.action == EVENT_ACTION_JOIN
        assert event_2.user == authorized_user
        assert event_2.to_phase_id == None

        assert authorized_user in class_room.attending.all()

    @pytest.mark.django_db
    def test_class_join_and_leave(self, authorized_user, class_room):
        class_room.join(authorized_user)
        assert class_room.events.all().count() == 1
        event = class_room.events.all()[0]
        assert event.action == EVENT_ACTION_JOIN
        assert event.user == authorized_user
        assert event.to_phase_id == None
        assert authorized_user in class_room.attending.all()

        class_room.leave(authorized_user)
        assert class_room.events.all().count() == 2
        event = class_room.events.all()[1]
        assert event.action == EVENT_ACTION_LEAVE
        assert event.user == authorized_user
        assert event.to_phase_id == None
        assert authorized_user not in class_room.attending.all()

    @pytest.mark.django_db
    def test_change_to_correct_phase(self, authorized_user, class_room):
        class_room.change_phase(authorized_user, class_room.course.phases.all()[1].id)
        assert class_room.events.all().count() == 1
        event = class_room.events.all()[0]
        assert event.action == EVENT_ACTION_CHANGE_PHASE
        assert event.user == authorized_user
        assert event.to_phase_id == class_room.course.phases.all()[1].id

