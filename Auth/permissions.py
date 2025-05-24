import environ
from django.core.mail import send_mail
from rest_framework import permissions

from Authentication.models import *

env = environ.Env()
environ.Env.read_env()

def send_email_global(subject,message,rcvr_email):
    from_email = env('EMAIL_HOST_USER')
    recipient_list = [rcvr_email]
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(str(e))

# class CustomPermission(permissions.BasePermission):


#     def has_permission(self, request, view):
#         if request.user.is_authenticated:
#             if request.user.is_superuser:
#                 return True
#             else:
#                 try:
#                     function_view = SystemModule.objects.get(function_name=str(view.__class__.__name__))
#                     if PreveliegePermission.objects.filter(user=request.user,group=function_view.group).exists():
#                         return True
#                     else:
#                         return False

#                 except Exception as e:
#                     print(e)
#                     return False

    # def has_object_permission(self, request, view, obj):
    #     if request.user.is_superuser:
    #         return True
    #
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    #
    #     if obj.author == request.user:
    #         return True
    #
    #     if request.user.is_staff and request.method not in self.edit_methods:
    #         return True
    #
    #     return False