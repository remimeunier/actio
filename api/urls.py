from django.urls import include, path

from .views import (
  ChangePhase,
  ClassRoomDetail,
  CourseDetail,
  CourseList,
  CreateClassRoom,
  JoinClassRoom
)


urlpatterns = [
    path("courses/", CourseList.as_view(), name="classes_list"),
    path("courses/<int:pk>", CourseDetail.as_view(), name="class_detail"),
    path("classrooms/<int:pk>", ClassRoomDetail.as_view(), name="class_room_detail"),
    path("classrooms/", CreateClassRoom.as_view(), name="create_class_room"),
    path("classrooms/<int:class_room_id>/change_phase", ChangePhase.as_view(), name="change_phase"),
    path("classrooms/<int:class_room_id>/join", JoinClassRoom.as_view(), name="join_class_room"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
