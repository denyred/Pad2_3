from rest_framework.permissions import BasePermission
import requests
from django.core.cache import cache
import os


def get_user_info(user_id):

    # Check the cache first
    cached_user_data = cache.get(f"user_{user_id}_data")
    if cached_user_data:
        print(f"CheckUserWithAuthenService: Using cached data for user#{user_id}")
        return cached_user_data

    try:
        # Make request to authenService to check user's existence and get fname and lname
        response = requests.get(
            f'{os.getenv('GW_BASE_URL')}authen/utilities/check?user_id={user_id}'
        )

        if response.status_code == 200:
            user_data = response.json()
            user_data['id'] = user_id
            cache_user_info(user_id, user_data)

            return user_data
    except requests.RequestException as e:
        print(f"utilities/check?user_id={user_id} request failed: {e}")

    return None

def cache_user_info(user_id, user_data):
    cache.set(f"user_{user_id}_data", user_data, timeout=3600)
    print(f"CheckUserWithAuthenService: Cached data for user#{user_id}")


class CheckUserWithAuthenService(BasePermission):

    def has_permission(self, request, view):
        try:
            try:
                user_id = int(request.headers.get('X-User'))
            except ValueError:
                return False
        except TypeError:
            return False

        user_data = get_user_info(user_id)
        if user_data:
            request.user_data = user_data
            return True
        
        return False