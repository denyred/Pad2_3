from django.urls import path
from .views import StatusView, SleepyView, CheckUserIdView


urlpatterns = [
    path('status', StatusView.as_view(), name='status'),
    path('sleepy', SleepyView.as_view(), name='sleepy'),
    path('check', CheckUserIdView.as_view(), name='check'),
]