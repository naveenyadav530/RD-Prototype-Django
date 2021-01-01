from django.shortcuts import redirect
from django.contrib.auth import logout
def authenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/dashboard")
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def staff_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            logout(request)
            return redirect("/")
    return wrapper_func

def super_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            logout(request)
            return redirect("/")
    return wrapper_func