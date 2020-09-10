from django.db.models import Prefetch
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

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
    queryset = ClassRoom.objects.select_related('course').prefetch_related(
        Prefetch('events', queryset=Event.objects.select_related('to_phase'))).all()
    serializer_class = ClassRoomSerializer

class JoinClassRoom(APIView):

    def post(self, _request, class_room_id):
        try:
            class_room = ClassRoom.objects.get(pk=class_room_id)
        except ClassRoom.DoesNotExist:
            return build_error_response(status.HTTP_404_NOT_FOUND, 'This Classroom do not exist')
        # Placeholder until User can join and leave
        e = Event(join='someone join', class_room=class_room)
        e.save()
        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)

class CreateClassRoom(APIView):

    def post(self, request):
        course_id = request.data.get('course_id')
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return build_error_response(status.HTTP_404_NOT_FOUND, 'This Course does not exist')
        class_room = ClassRoom(course=course)
        class_room.save()
        # Placeholder until User can join and leave
        e = Event(join='someone join', class_room=class_room)
        e.save()

        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)

class ChangePhase(APIView):

    def post(self, request, class_room_id):
        to_phase_id = request.data.get('to_phase_id', None)
        if to_phase_id is None:
            return build_error_response(status.HTTP_400_BAD_REQUEST, 'No phase ID rquested')
        try:
            class_room = ClassRoom.objects.get(pk=class_room_id)
        except ClassRoom.DoesNotExist:
            return build_error_response(status.HTTP_404_NOT_FOUND, 'This Class did not start')
        e = Event(to_phase_id=to_phase_id, class_room=class_room)
        e.save()
        return Response(ClassRoomSerializer(class_room).data, status.HTTP_200_OK)
