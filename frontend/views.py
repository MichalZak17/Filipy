from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from backend.utils import get_spotify_access_token


@login_required
def index_view(request):
    """
    Render the index page.
    """
    return render(request, "index.html")


@csrf_protect
def login_view(request):
    """
    Handles the login view for the application.

    This view function handles both GET and POST requests for user login.
    If the user is already authenticated, they are redirected to the home page.
    For POST requests, it attempts to authenticate the user with the provided email and password.
    If authentication is successful, the user is logged in and redirected to the home page.
    If authentication fails, an error message is returned as a JSON response.
    For GET requests, it renders the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to the home page if the user is authenticated or after a successful login.
        JsonResponse: Returns an error message if authentication fails.
        HttpResponse: Renders the login page for GET requests.
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return JsonResponse({"error": "Invalid email or password."})

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return JsonResponse({"error": "Invalid email or password."})

    else:
        return render(request, "login.html")


def forgotten_password_view(request):
    """
    Render the forgotten password page.
    """
    return render(request, "404.html")


def logout_view(request):
    """
    Handles the logout view for the application.

    This view function logs out the user and redirects them to the home page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to the home page after logging out.
    """
    logout(request)
    return redirect("login")
