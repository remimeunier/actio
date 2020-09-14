from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import EVENT_ACTION_CHANGE_PHASE, EVENT_ACTION_JOIN, EVENT_ACTION_LEAVE
from .models import ClassRoom, Course, Event
from .serializers import ClassRoomSerializer, CourseSerializer
from .utils import build_error_response


class CourseList(generics.ListAPIView):
    queryset = Course.objects.prefetch_related('phases').order_by('title').all()
    serializer_class = CourseSerializer


class CourseDetail(generics.RetrieveAPIView):
    queryset = Course.objects.prefetch_related('phases').all()
    serializer_class = CourseSerializer


class ClassRoomDetail(generics.RetrieveAPIView):
    queryset = ClassRoom.objects.select_related('course').prefetch_related('attending',
        Prefetch('events', queryset=Event.objects.select_related('to_phase', 'user'))).all()
    serializer_class = ClassRoomSerializer


class CreateClassRoom(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        course_id = request.data.get('course_id')
        if course_id is None:
            return build_error_response(status.HTTP_400_BAD_REQUEST, 'No phase ID rquested')
        course = get_object_or_404(Course.objects.select_related('default_phase'), pk=course_id)
        # Create class room
        class_room = ClassRoom.kick_off(course, request.user)

        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)

class BaseClassRoomAction(APIView):
    permission_classes = (IsAuthenticated,)

    def retrieve_class_room(self, class_room_id):
        return get_object_or_404(ClassRoom.objects.select_related('course'), pk=class_room_id)


class JoinClassRoom(BaseClassRoomAction):

    def post(self, request, class_room_id):
        class_room = self.retrieve_class_room(class_room_id).join(request.user)
        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)


class LeaveClassRoom(BaseClassRoomAction):

    def post(self, request, class_room_id):
        class_room = self.retrieve_class_room(class_room_id).leave(request.user)
        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)


class ChangePhase(BaseClassRoomAction):

    def post(self, request, class_room_id):
        to_phase_id = request.data.get('to_phase_id', None)
        if to_phase_id is None:
            return build_error_response(status.HTTP_400_BAD_REQUEST, 'Need a phase_id')

        class_room = self.retrieve_class_room(class_room_id)
        if int(to_phase_id) not in [phase.id for phase in class_room.course.phases.all()]:
            return build_error_response(status.HTTP_400_BAD_REQUEST, 'Can\'t go to this phase')

        class_room.change_phase(request.user, to_phase_id)
        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)
