from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
  ChangePhase,
  ClassRoomDetail,
  CourseDetail,
  CourseList,
  CreateClassRoom,
  JoinClassRoom,
  LeaveClassRoom
)


urlpatterns = [
    path("courses/", CourseList.as_view(), name="classes_list"),
    path("courses/<int:pk>", CourseDetail.as_view(), name="class_detail"),
    path("classrooms/<int:pk>", ClassRoomDetail.as_view(), name="class_room_detail"),
    path("classrooms/", CreateClassRoom.as_view(), name="create_class_room"),
    path("classrooms/<int:class_room_id>/change_phase", ChangePhase.as_view(), name="change_phase"),
    path("classrooms/<int:class_room_id>/join", JoinClassRoom.as_view(), name="join_class_room"),
    path("classrooms/<int:class_room_id>/leave", LeaveClassRoom.as_view(), name="leave_class_room"),
    path('auth/', obtain_auth_token, name='api_token_auth')
]
