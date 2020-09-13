from django.db.models import Prefetch
from django.http import Http404
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

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return  build_error_response(status.HTTP_404_NOT_FOUND, 'This Course does not exist')

class ClassRoomDetail(generics.RetrieveAPIView):
    queryset = ClassRoom.objects.select_related('course').prefetch_related(
        Prefetch('events', queryset=Event.objects.select_related('to_phase'))).all()
    serializer_class = ClassRoomSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Http404:
            return  build_error_response(status.HTTP_404_NOT_FOUND, 'This classroom does not exist')

class CreateClassRoom(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        course_id = request.data.get('course_id')
        if course_id is None:
            return build_error_response(status.HTTP_400_BAD_REQUEST, 'No phase ID rquested')
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return build_error_response(status.HTTP_404_NOT_FOUND, 'This Course does not exist')
        # Create class room
        class_room = ClassRoom.kick_off(course, request.user)

        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)

class JoinClassRoom(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, class_room_id):
        try:
            class_room = ClassRoom.objects.get(pk=class_room_id)
        except ClassRoom.DoesNotExist:
            return build_error_response(status.HTTP_404_NOT_FOUND, 'This Classroom does not exist')
        class_room = class_room.join(request.user)
        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)

class LeaveClassRoom(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, class_room_id):
        try:
            class_room = ClassRoom.objects.get(pk=class_room_id)
        except ClassRoom.DoesNotExist:
            return build_error_response(status.HTTP_404_NOT_FOUND, 'This Classroom does not exist')
        class_room = class_room.leave(request.user)
        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)

class ChangePhase(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, class_room_id):
        to_phase_id = request.data.get('to_phase_id', None)

        if to_phase_id is None:
            return build_error_response(status.HTTP_400_BAD_REQUEST, 'Need a phase_id')
        try:
            class_room = ClassRoom.objects.get(pk=class_room_id)
        except ClassRoom.DoesNotExist:
            return build_error_response(status.HTTP_404_NOT_FOUND, 'This Class did not start')
        if int(to_phase_id) not in [phase.id for phase in class_room.course.phases.all()]:
            return build_error_response(status.HTTP_404_NOT_FOUND, 'This phase does not exist')
        class_room.change_phase(request.user, to_phase_id)
        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)
