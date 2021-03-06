from datetime import datetime, timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models

from .constants import (
    EVENT_ACTION_CHANGE_PHASE,
    EVENT_ACTION_CHOICES,
    EVENT_ACTION_JOIN,
    EVENT_ACTION_LEAVE
)


class Phase(models.Model):
    title = models.CharField(max_length=60)
    timer = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Course(models.Model):
    title = models.CharField(max_length=60)
    phases = models.ManyToManyField(Phase, blank=True)
    default_phase = models.ForeignKey(Phase, null= True, on_delete=models.SET_NULL,
                                      related_name='start_of_course')

    def __str__(self):
        return self.title

class ClassRoom(models.Model):
    course = models.ForeignKey(Course, on_delete=models.RESTRICT, related_name='class_rooms')
    attending = models.ManyToManyField(User, blank=True, related_name='class_rooms')

    @classmethod
    def kick_off(cls, course, user):
        class_room = cls(course=course)
        class_room.save()
        class_room.change_phase(user, course.default_phase.id)
        class_room.join(user)
        return class_room

    def join(self, user):
        self.attending.add(user)
        self.save()
        Event(action=EVENT_ACTION_JOIN, class_room=self, user=user, timer=self._get_event_timer()).save()
        return self

    def leave(self, user):
        self.attending.remove(user)
        self.save()
        Event(action=EVENT_ACTION_LEAVE, class_room=self, user=user, timer=self._get_event_timer()).save()
        return self

    def change_phase(self, user, phase_id):
        Event(action=EVENT_ACTION_CHANGE_PHASE, class_room=self, user=user,
              to_phase_id=phase_id, timer=self._get_event_timer()).save()
        return self

    def _get_event_timer(self):
        last_event = self.events.filter(to_phase__isnull=False).order_by('created_at').last()
        if last_event is None:
            return 0
        elif last_event.to_phase.timer == True:
            return last_event.timer + (datetime.now(timezone.utc) - last_event.created_at).total_seconds()
        else:
            return last_event.timer

    def __str__(self):
        return 'class room of : {}'.format(self.course.title)

class Event(models.Model):
    action = models.IntegerField(choices=EVENT_ACTION_CHOICES,
                                 blank=False, null=False,
                                 default=EVENT_ACTION_CHANGE_PHASE)
    to_phase = models.ForeignKey(Phase, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    timer = models.IntegerField(blank=False, null=False, default=0)

    def __str__(self):
        return 'action {} at {} for {}'.format(self.action, self.created_at, self.class_room.id)
