from django.urls import path
from .views import ChatListView, ChatDeleteView, StartChatView, ChatListMyView, ChatConnectView


urlpatterns = [
    path('list/all', ChatListView.as_view(), name='list-all'),
    path('list/my', ChatListMyView.as_view(), name='list-my'),
    path('delete/<int:id>', ChatDeleteView.as_view(), name='delete'),
    path('start', StartChatView.as_view(), name='start'),
    path('connect', ChatConnectView.as_view(), name='connect'),
]