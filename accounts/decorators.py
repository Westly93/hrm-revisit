from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def user_not_authenticated(function=None, redirect_url='/'):
    """
    Decorator for views that checks that the user is NOT logged in, redirecting
    to the homepage if necessary by default.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator


def is_admin(function=None):
    """
    Decorator for views that checks if the user is an admin.
    If the user is not an admin, it returns a 403 Forbidden response.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if not request.user.is_admin and not request.user.is_staff:
                    return HttpResponseForbidden('You do not have permission to access this page.')
            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def is_active(function=None):
    """
    Decorator for views that checks if the user is an admin.
    If the user is not an admin, it returns a 403 Forbidden response.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                if not request.user.is_active:
                    return redirect('accounts:in_active')
            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator
