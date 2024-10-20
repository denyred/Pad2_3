from django.urls import path
from .views import UserListView, UserDeleteView, EmployeeListView, PatchEmployeeRatingView

urlpatterns = [
    path('list/all', UserListView.as_view(), name='users-list-all'),
    path('list/employee', EmployeeListView.as_view(), name='users-list-employee'),
    path('patch/rating', PatchEmployeeRatingView.as_view(), name='users-patch-rating'),
    path('delete/<int:id>', UserDeleteView.as_view(), name='users-delete'),
]