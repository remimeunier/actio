import pytest
import json
from api.tests.factory import request_factory
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate

from api.constants import (
    EVENT_ACTION_CHANGE_PHASE,
    EVENT_ACTION_JOIN,
    EVENT_ACTION_LEAVE
)
from api.tests.fixtures import authorized_user, course, class_room, phase
from api.views import (
  ChangePhase,
  ClassRoomDetail,
  CourseDetail,
  CourseList,
  CreateClassRoom,
  JoinClassRoom,
  LeaveClassRoom
)

class TestCourseList:

    @pytest.mark.django_db
    def test_course_list_success(self, request_factory, course):
        request = request_factory.get('courses')
        view = CourseList.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['id'] == course.id

class TestCourseDetail:

    @pytest.mark.django_db
    def test_course_detail_success(self, request_factory, course):
        request = request_factory.get(f'/courses/{course.id}/')
        view = CourseDetail.as_view()
        response = view(request, pk=course.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == course.id
        assert response.data['title'] == course.title
        assert response.data['phases'][0]['id'] == course.phases.first().id
        assert response.data['phases'][1]['id'] == course.phases.last().id
        assert response.data['class_rooms'] == []

    @pytest.mark.django_db
    def test_course_detail_wrong_id(self, request_factory):
        request = request_factory.get(f'/courses/1000/')
        view = CourseDetail.as_view()
        response = view(request, pk=1000)
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestClassRoomDetail:

    @pytest.mark.django_db
    def test_class_room_detail_success(self, request_factory, class_room):
        request = request_factory.get(f'/classroom/{class_room.id}/')
        view = ClassRoomDetail.as_view()
        response = view(request, pk=class_room.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == class_room.id
        assert response.data['events'] == []
        assert response.data['attending'] == []

    @pytest.mark.django_db
    def test_class_room_detail_success(self, request_factory):
        request = request_factory.get(f'/classroom/{1000}/')
        view = ClassRoomDetail.as_view()
        response = view(request, pk=1000)
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestCreateClassRoom:

    @pytest.mark.django_db
    def test_create_class_room_no_user(self, request_factory):
        request = request_factory.post(f'/classroom/')
        view = CreateClassRoom.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_class_room_success(self, request_factory, authorized_user, course):
        request = request_factory.post(f'/classroom/', {'course_id': course.id},
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = CreateClassRoom.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id']
        assert len(response.data['events']) == 2
        assert response.data['events'][0]['action'] == EVENT_ACTION_CHANGE_PHASE
        assert response.data['events'][0]['user']['id'] == authorized_user.id
        assert response.data['events'][0]['to_phase']['id'] == course.default_phase.id
        assert response.data['events'][1]['action'] == EVENT_ACTION_JOIN
        assert response.data['events'][1]['user']['id'] == authorized_user.id
        assert response.data['events'][1]['to_phase'] == None

        assert len(response.data['attending']) == 1
        assert response.data['attending'][0]['id'] == authorized_user.id

    @pytest.mark.django_db
    def test_create_class_room_wrong_param_value(self, request_factory, authorized_user):
        request = request_factory.post(f'/classroom/', {'course_id': 10000},
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = CreateClassRoom.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_create_class_room_wrong_param_key(self, request_factory, authorized_user, course):
        request = request_factory.post(f'/classroom/', {'wrong_key': course.id},
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = CreateClassRoom.as_view()
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

class TestJoinclassRoom:

    @pytest.mark.django_db
    def test_join_class_room_no_user(self, request_factory, class_room):
        request = request_factory.post(f'/classroom/{class_room.id}/')
        view = JoinClassRoom.as_view()
        response = view(request, class_room_id=class_room.id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_join_class_room_success(self, request_factory, authorized_user, class_room):
        request = request_factory.post(f'/classroom/{class_room.id}/',
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = JoinClassRoom.as_view()
        response = view(request, class_room_id=class_room.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id']
        assert len(response.data['events']) == 1
        assert response.data['events'][0]['action'] == EVENT_ACTION_JOIN
        assert response.data['events'][0]['user']['id'] == authorized_user.id
        assert len(response.data['attending']) == 1
        assert response.data['attending'][0]['id'] == authorized_user.id

    @pytest.mark.django_db
    def test_join_class_room_wrong_param_value(self, request_factory, authorized_user):
        request = request_factory.post(f'/classroom/{10000}/',
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = JoinClassRoom.as_view()
        response = view(request, class_room_id=10000)
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestLeaveClassRoom:

    @pytest.mark.django_db
    def test_leave_class_room_no_user(self, request_factory, class_room):
        request = request_factory.post(f'/classroom/{class_room.id}/')
        view = LeaveClassRoom.as_view()
        response = view(request, class_room_id=class_room.id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_leave_class_room_success(self, request_factory, authorized_user, class_room):
        class_room.attending.add(authorized_user)
        class_room.save()
        request = request_factory.post(f'/classroom/{class_room.id}/',
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = LeaveClassRoom.as_view()
        response = view(request, class_room_id=class_room.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id']
        assert len(response.data['events']) == 1
        assert response.data['events'][0]['action'] == EVENT_ACTION_LEAVE
        assert response.data['events'][0]['user']['id'] == authorized_user.id
        assert len(response.data['attending']) == 0

    @pytest.mark.django_db
    def test_join_class_room_wrong_param_value(self, request_factory, authorized_user):
        request = request_factory.post(f'/classroom/{10000}',
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = LeaveClassRoom.as_view()
        response = view(request, class_room_id=10000)
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestChangePhase:

    @pytest.mark.django_db
    def test_change_phase_no_user(self, request_factory, class_room):
        request = request_factory.post(f'/classroom/{class_room.id}/')
        view = ChangePhase.as_view()
        response = view(request, class_room_id=class_room.id)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_change_phase_wrong_class_room_id(self, request_factory, authorized_user, class_room):
        request = request_factory.post(f'/classroom/{1000}/',
          {'to_phase_id': class_room.course.phases.first()},
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = ChangePhase.as_view()
        response = view(request, class_room_id=1000)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_change_phase_wrong_param_value(self, request_factory, authorized_user, class_room):
        request = request_factory.post(f'/classroom/{class_room.id}/', {'to_phase_id': 1000},
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = ChangePhase.as_view()
        response = view(request, class_room_id=1000)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_change_phase_wrong_param_key(self, request_factory, authorized_user, class_room):
        to_phase = class_room.course.phases.first()
        request = request_factory.post(f'/classroom/{class_room.id}/', {'wrong_key': to_phase},
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = ChangePhase.as_view()
        response = view(request, class_room_id=class_room.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_phase_success(self, request_factory, authorized_user, class_room):
        to_phase = class_room.course.phases.first()
        request = request_factory.post(f'/classroom/{class_room.id}/', {'to_phase_id': to_phase.id},
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = ChangePhase.as_view()
        response = view(request, class_room_id=class_room.id)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['events']) == 1
        assert response.data['events'][0]['to_phase']['id'] == to_phase.id
        assert response.data['events'][0]['user']['id'] == authorized_user.id

    def test_change_phase_wrong_phase(self, request_factory, authorized_user, class_room, phase):
        request = request_factory.post(f'/classroom/{class_room.id}/', {'to_phase_id': phase.id},
          HTTP_AUTHORIZATION='Token {}'.format(Token.objects.create(user=authorized_user)))
        view = ChangePhase.as_view()
        response = view(request, class_room_id=class_room.id)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
