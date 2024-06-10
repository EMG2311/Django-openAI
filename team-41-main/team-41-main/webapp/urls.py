from django.urls import path
from . import views


urlpatterns = [
    path('', views.inputSkill),
    path('showKnownSkillsForm', views.showKnownSkillsForm),
    path('roadmap', views.roadmap),
    path('learn/theory', views.theory),
    path('learn/quiz', views.quiz),
    path('learn/task', views.task),
    path('learn/task/check', views.checkTask),
]
