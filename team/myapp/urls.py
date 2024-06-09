from django.urls import path
from . import views
urlpatterns = [
    path('',views.inputSkill),
    path('showSkills',views.showSkills),
    path('taskForSkill',views.taskForSkill),

    
]