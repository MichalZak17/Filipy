from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.contrib.auth.models import User

from backend.models import Playlist

@login_required
def index_view(request):
    """Renders the index page.

    Args:
        request: The HTTP request object.

    Returns:
        An HttpResponse object that renders the "index.html" template.
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
    If authentication fails, it re-renders the login page with an error message.
    For GET requests, it renders the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Redirects to the home page if the user is authenticated or after a successful login.
        HttpResponse: Renders the login page, potentially with an error message.
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            return render(request, "login.html", {"error": "Please enter both email and password."})

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Invalid email or password."})

    else:
        return render(request, "login.html")


def forgotten_password_view(request):
    """
    Render the forgotten password page.
    """
    return render(request, "404.html")


@login_required
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


@login_required
def spotify_playlists(request):
    """
    Renders a page displaying Spotify playlists for the logged-in user.

    This view fetches all `Playlist` objects associated with the currently
    authenticated user, orders them by their creation date in descending
    order, and then renders the `spotify_playlists.html` template,
    passing the playlists as context.

    Args:
        request: The HttpRequest object.

    Returns:
        HttpResponse: An HttpResponse object rendering the
                    `spotify_playlists.html` template with the user's
                    playlists.
    """
    playlists = Playlist.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "spotify_playlists.html", {"playlists": playlists})


@login_required
def settings_view(request):
    """
    Render the settings page.
    """
    return render(request, "404.html")


@csrf_protect
@transaction.atomic
def signup_view(request):
    """
    Handles user registration.

    If the user is already authenticated, they are redirected to the 'home' page.

    For POST requests:
        - Retrieves and validates 'email' and 'password' from the request.
        - If validation fails, returns a 400 JSON response with an error message.
        - Attempts to create a new user with the provided credentials.
        - If user creation is successful:
            - Authenticates and logs in the new user.
            - Returns a 201 JSON response with a success message.
        - If a user with the given email already exists (IntegrityError),
        returns a 409 JSON response with an error message.
        - For any other exception during user creation, returns a 500 JSON
        response with the exception message.

    For GET requests (or any method other than POST):
        - Renders the 'signup.html' template.

    Decorators:
        - @csrf_protect: Ensures CSRF protection for the view.
        - @transaction.atomic: Wraps the user creation process in a database transaction.
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            return JsonResponse({"error": "Email and password are required."}, status=400)

        try:
            user = User.objects.create_user(
                username=email, email=email, password=password, is_active=True
            )

            user = authenticate(request, username=email, password=password)
            login(request, user)

            return JsonResponse({"message": "User created successfully."}, status=201)

        except IntegrityError:
            return JsonResponse({"error": "A user with that email already exists."}, status=409)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=500)

    return render(request, "signup.html")
