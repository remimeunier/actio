from django.contrib.auth.models import User
from rest_framework import serializers

from .constants import EVENT_ACTION_CHOICES
from .models import ClassRoom, Course, Event, Phase


class PhaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Phase
        fields = ('id', 'title', 'timer')

class CourseSerializer(serializers.HyperlinkedModelSerializer):
    phases = PhaseSerializer(many=True, read_only=True)
    class_rooms = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'phases', 'class_rooms')

class CurrentUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'id')

class EventSerializer(serializers.HyperlinkedModelSerializer):
    to_phase = PhaseSerializer(many=False, read_only=True)
    user = CurrentUserSerializer(many=False, read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'to_phase', 'action', 'created_at', 'user')

class ClassRoomSerializer(serializers.HyperlinkedModelSerializer):
    course = CourseSerializer(many=False, read_only=True)
    events = EventSerializer(many=True, read_only=True)
    attending = CurrentUserSerializer(many=True, read_only=True)

    class Meta:
        model = ClassRoom
        fields = ('id', 'course', 'events', 'attending')
