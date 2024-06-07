from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import AdminUser  # Import your custom user model
from django.contrib.auth.hashers import make_password

class CINAuthBackend(BaseBackend):
    def authenticate(self, request, cin=None, password=None):
        try:
            user = AdminUser.objects.get(cin=cin)
            if check_password(password, user.password):
                return user
        except AdminUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return AdminUser.objects.get(pk=user_id)
        except AdminUser.DoesNotExist:
            return None
