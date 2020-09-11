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

    def __str__(self):
        return self.title

class ClassRoom(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='class_rooms')
    attending = models.ManyToManyField(User, blank=True, related_name='class_rooms')

    @classmethod
    def kick_off(cls, course, user):
        class_room = cls(course=course)
        class_room.save()
        # start default phase
        class_room.join(user)
        return class_room

    def join(self, user):
        self.attending.add(user)
        self.save()
        Event(action=EVENT_ACTION_JOIN, class_room=self, user=user).save()
        return self

    def leave(self, user):
        self.attending.remove(user)
        self.save()
        Event(action=EVENT_ACTION_LEAVE, class_room=self, user=user).save()
        return self

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

    def __str__(self):
        return 'to {} at {} for {}'.format(self.to_phase.title, self.created_at, self.class_room.id)
