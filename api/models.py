from django.db import models


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

    def __str__(self):
        return 'class room of : {}'.format(self.course.title)

class Event(models.Model):
    to_phase = models.ForeignKey(Phase, on_delete=models.CASCADE, null=True)
    join = models.CharField(max_length=60, null=True)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'to {} at {} for {}'.format(self.to_phase.title, self.created_at, self.class_room.id)
