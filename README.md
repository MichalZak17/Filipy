# Filipy - Mood-Based Spotify Playlist Generator

Filipy is a web application that creates personalized Spotify playlists based on your mood or a descriptive prompt.

[![License](https://img.shields.io/badge/License-Closed%20Source-red.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg?style=flat-square)](#tech-stack)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg?style=flat-square)](#tech-stack)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.16-orange.svg?style=flat-square)](#tech-stack)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-lightgrey.svg?style=flat-square)](#tech-stack)
[![Docker](https://img.shields.io/badge/Docker-Supported-blueviolet.svg?style=flat-square)](#installation)
![Last Commit](https://img.shields.io/github/last-commit/MichalZak17/filipy?style=flat-square) -->

## Overview

Filipy is a web application designed to bridge the gap between your current mood and the perfect soundtrack. By integrating with the Spotify API, Filipy allows users to input a mood or a descriptive prompt (e.g., "energetic electronic music for coding") and, in return, receive a custom-generated playlist added directly to their Spotify account.

The project leverages Django and Django REST Framework for a robust backend, while the frontend is built with Django templates, Bootstrap 5, and JavaScript. The entire application is containerized using Docker for streamlined development and deployment.

**Problem it solves:** Simplifies the discovery of mood-matching music on Spotify.
**Target audience:** Spotify users looking for a quick and intuitive way to create playlists tailored to their specific moods or activities.
**Inspiration**: This project draws inspiration from [Moodify by mahnoorshafi](https://github.com/mahnoorshafi/Moodify).

## Features

*   **User Authentication**: Secure user registration and login system using Django's built-in authentication, supplemented by JWT for API access.
*   **Spotify Integration**:
    *   OAuth2 flow to securely connect a user's Spotify account.
    *   Efficient management of Spotify API access and refresh tokens.
*   **Mood-Based Playlist Creation**:
    *   Users can input a mood or a descriptive prompt (e.g., "upbeat pop for a morning workout").
    *   The backend processes this prompt to generate a list of relevant tracks using the Spotify API.
    *   Automatically creates a new private playlist in the user's Spotify account with these tracks.
*   **Playlist Management**:
    *   View a list of playlists created via Filipy.
    *   Direct links to open these playlists on Spotify.
*   **RESTful API**: A well-defined API for managing user authentication, Spotify integration, and playlists.
*   **Responsive Frontend**: User interface built with Bootstrap 5, ensuring adaptability across different screen sizes.
*   **Containerized**: Fully containerized with Docker and Docker Compose for consistent development and production environments and easy setup.

## Tech Stack

*   **Backend**:
    *   Python 3.11
    *   Django 5.2
    *   Django REST Framework 3.16
    *   Spotipy (Spotify API client library)
    *   Psycopg2 (PostgreSQL adapter)
    *   `djangorestframework-simplejwt` (for JWT authentication)
*   **Frontend**:
    *   HTML5
    *   CSS3 (Bootstrap 5)
    *   JavaScript (ES6 Modules)
*   **Database**:
    *   PostgreSQL
*   **Caching/Task Queues (Dependencies present, for future use)**:
    *   Redis
    *   Celery
*   **Containerization**:
    *   Docker
    *   Docker Compose
*   **Authentication Mechanisms**:
    *   Django Session Authentication
    *   JWT (JSON Web Tokens)
    *   Spotify OAuth2
*   **Static Files Serving**:
    *   WhiteNoise

## Architecture

Filipy employs a monolithic architecture based on the Django framework, with a clear separation of concerns:

*   **`backend/` (Django App)**: Houses the core logic.
    *   `api/`: Contains API views (using Django REST Framework) and serializers for handling requests related to authentication, playlists, and Spotify interactions.
    *   `models.py`: Defines database models such as `SpotifyAccount` (for storing user Spotify tokens) and `Playlist` (for playlist metadata and mood prompts).
    *   `utils/spotify_helpers.py`: Contains helper functions for interacting with the Spotify API via Spotipy (e.g., creating playlists, searching tracks, adding tracks).
    *   `urls.py`: Defines API endpoint routes.
*   **`frontend/` (Django App)**: Responsible for the user interface.
    *   `templates/`: Contains HTML templates, including `base.html` (main layout), [`index.html`](/home/me/Filipy/frontend/templates/index.html) (landing page), authentication pages (`login.html`, `signup.html`), and `spotify_playlists.html` (for playlist creation and listing).
    *   `views.py`: Django views that render the HTML templates.
    *   `static/`: App-specific static files.
*   **`software/` (Django Project)**:
    *   `settings.py`: Main Django project settings, including database configuration, installed apps, and middleware.
    *   `urls.py`: Root URL configuration, delegating to app-specific `urls.py` files.
*   **`static/` (Project Root)**: Global static assets (CSS, JavaScript, images) served by WhiteNoise.
*   **Docker**: `Dockerfile` defines the image for the web application, and `docker-compose.yml` orchestrates the multi-container setup (web, database, Redis).

Data Flow for Playlist Creation:
1.  User authenticates and connects their Spotify account.
2.  User submits a mood prompt via the frontend.
3.  Frontend JavaScript makes an API call to the `/api/playlists/` endpoint.
4.  The backend API view:
    a.  Validates the request.
    b.  Saves initial playlist data to the PostgreSQL database.
    c.  Uses `spotify_helpers.py` to communicate with the Spotify API:
        i.  Creates a new playlist on Spotify.
        ii. Generates track recommendations based on the mood prompt.
        iii.Adds recommended tracks to the newly created Spotify playlist.
    d.  Updates the local playlist record with the `spotify_id` and other relevant details.
5.  The frontend can then display the new playlist and a link to it on Spotify.

## Installation

You can run Filipy using Docker (recommended) or a Python virtual environment.

### Prerequisites

*   Git
*   Docker Engine and Docker Compose (for Docker setup)
*   Python 3.11 and PostgreSQL (for virtual environment setup)
*   A `.env` file in the project root (see [Configuration](#configuration) section).

### 1. Clone the Repository

```bash
git clone https://github.com/MichalZak17/Filipy.git
cd Filipy
```

### 2. Create `.env` File
Copy the example below or create a new `.env` file in the project root (`/home/me/Filipy/.env`). Populate it with your credentials and settings. See the [Configuration](#configuration) section for details.

### Option A: Docker Setup (Recommended)

1.  **Build and run the application using Docker Compose**:
    ```bash
    docker-compose up --build -d
    ```
    The `-d` flag runs the containers in detached mode.

2.  **Apply database migrations (if not automatically handled by entrypoint)**:
    The provided `docker-compose.yml` and `Dockerfile` attempt to run migrations on startup. If you need to run them manually:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

3.  **Create a superuser (optional, for Django Admin)**:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

4.  **Access the application**:
    *   Web Application: `http://localhost:8000`
    *   Django Admin: `http://localhost:8000/django-admin/`
    *   pgAdmin (Database Admin Tool): `http://localhost:5050` (credentials from `.env`)

### Option B: Python Virtual Environment Setup

1.  **Ensure Python 3.11 and PostgreSQL are installed and running.**

2.  **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the PostgreSQL database**:
    *   Create a PostgreSQL database (e.g., `software_db`).
    *   Create a PostgreSQL user (e.g., `usr_x29Aq3Lz9pR7Mvt`) with a password.
    *   Grant the user privileges to the database.
    *   Ensure your `.env` file has the correct `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`.

5.  **Apply database migrations**:
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser (optional)**:
    ```bash
    python manage.py createsuperuser
    ```

7.  **Collect static files (for development if DEBUG=False, or for production setup)**:
    ```bash
    python manage.py collectstatic
    ```

8.  **Run the development server**:
    ```bash
    python manage.py runserver # Usually on http://localhost:8000
    ```

## Configuration

Create a `.env` file in the project root (`/home/me/Filipy/.env`) with the following essential variables:

```env
# Django
SECRET_KEY=your_very_secret_django_secret_key_here # Important: Keep this secret!
DEBUG=True # Set to False in production

# PostgreSQL Database
POSTGRES_DB=software_db
POSTGRES_USER=usr_x29Aq3Lz9pR7Mvt
POSTGRES_PASSWORD=your_secure_postgres_password
# For local development with Docker, POSTGRES_HOST is typically the service name (e.g., 'db')
# For virtual env setup, it might be 'localhost' or an IP address.
# POSTGRES_HOST=db # Example for Docker
# POSTGRES_PORT=5432 # Default PostgreSQL port

# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
# Ensure this redirect URI is registered in your Spotify Developer Dashboard
# For Docker setup (default port 8888):
SPOTIFY_REDIRECT_URI=http://localhost:8888/api/auth/spotify/callback/
# For local virtual env setup (default port 8000):
# SPOTIFY_REDIRECT_URI=http://localhost:8000/api/auth/spotify/callback/

# pgAdmin (Optional, for database management via pgAdmin container in Docker setup)
PGADMIN_DEFAULT_EMAIL=your_pgadmin_email@example.com
PGADMIN_DEFAULT_PASSWORD=your_secure_pgadmin_password
```

**Important Note on `SPOTIFY_REDIRECT_URI`**:
The `SPOTIFY_REDIRECT_URI` in your `.env` file **must exactly match** one of the Redirect URIs you've configured in your application settings on the Spotify Developer Dashboard.
*   If running with Docker Compose as per `docker-compose.yml`, the application is typically accessible at `http://localhost:8000`.
*   If running with `python manage.py runserver` locally, it's often `http://localhost:8000`. Adjust the port accordingly.

## Usage

### Starting the Application

*   **Docker**:
    ```bash
    docker-compose up -d
    ```
    Access at `http://localhost:8000`.

*   **Python Virtual Environment**:
    ```bash
    python manage.py runserver
    ```
    Access at `http://localhost:8000` (or the port specified).

### Main Features

1.  **Register/Login**: Create an account or log in to access Filipy.
2.  **Connect to Spotify**: Navigate to the playlist page (e.g., `/spotify-playlists/`) and click the "Connect to Spotify" button. You'll be redirected to Spotify for authorization.
3.  **Create a Playlist**:
    *   Once connected, use the form on the playlist page.
    *   Enter a **Playlist Name**.
    *   Optionally, add a **Description**.
    *   Provide a **Mood Prompt** (e.g., "Chill vibes for a rainy afternoon", "High-energy workout mix").
    *   Click "Create Playlist".
4.  **View Playlists**: Your created playlists will be listed on the page, with links to open them directly on Spotify.

### Common Management Commands

*   Apply database migrations:
    *   Docker: `docker-compose exec web python manage.py migrate`
    *   Virtual Env: `python manage.py migrate`
*   Create a superuser:
    *   Docker: `docker-compose exec web python manage.py createsuperuser`
    *   Virtual Env: `python manage.py createsuperuser`
*   Collect static files (primarily for production or when `DEBUG=False`):
    *   Docker: `docker-compose exec web python manage.py collectstatic --noinput`
    *   Virtual Env: `python manage.py collectstatic --noinput`

## API Reference

The API is accessible under the `/api/` prefix. Most endpoints require JWT authentication in the `Authorization` header (`Bearer <your_access_token>`).

### Authentication

*   **`POST /api/token/`**: Obtain JWT token pair.
    *   **Request Body**:
        ```json
        {
            "username": "user@example.com",
            "password": "password123"
        }
        ```
    *   **Response (Success 200 OK)**:
        ```json
        {
            "refresh": "your_refresh_token",
            "access": "your_access_token"
        }
        ```
*   **`POST /api/token/refresh/`**: Refresh JWT access token.
    *   **Request Body**:
        ```json
        {
            "refresh": "your_refresh_token"
        }
        ```
    *   **Response (Success 200 OK)**:
        ```json
        {
            "access": "new_access_token"
        }
        ```
*   **`GET /api/token/session/`**: (Requires active Django session) Obtain JWT from session. Useful for frontend to get token after session-based login.
    *   **Response (Success 200 OK)**:
        ```json
        {
            "access": "your_access_token"
        }
        ```

### Spotify Authentication

*   **`GET /api/auth/spotify/login/`**: (Requires JWT/Session Auth) Get the Spotify authorization URL.
    *   **Response (Success 200 OK)**:
        ```json
        {
            "url": "https://accounts.spotify.com/authorize?client_id=..."
        }
        ```
    The frontend should redirect the user to this URL.
*   **`GET /api/auth/spotify/callback/?code=...&state=...`**: Handles the callback from Spotify after user authorization.
    *   This endpoint is typically redirected to by Spotify.
    *   It exchanges the `code` for Spotify tokens, updates the user's `SpotifyAccount` model, and then redirects the user (e.g., to `/spotify-playlists/`) on success.

### Playlists

Base URL: `/api/playlists/` (Requires JWT/Session Auth)

*   **`GET /api/playlists/`**: List all playlists for the authenticated user.
    *   **Response (Success 200 OK)**:
        ```json
        [
            {
                "id": 1,
                "name": "My Chill Vibes",
                "description": "Perfect for relaxing.",
                "mood_prompt": "chill instrumental music",
                "spotify_id": "spotify_playlist_id_123",
                "created_at": "2025-06-13T10:00:00Z",
                "spotify_url": "https://open.spotify.com/playlist/spotify_playlist_id_123"
            }
        ]
        ```
*   **`POST /api/playlists/`**: Create a new playlist.
    *   **Request Body**:
        ```json
        {
            "name": "My Awesome Playlist",
            "description": "Optional description for the playlist",
            "mood_prompt": "energetic electronic music for coding"
        }
        ```
    *   **Response (Success 201 Created)**:
        ```json
        {
            "id": 2,
            "name": "My Awesome Playlist",
            "description": "Optional description for the playlist",
            "mood_prompt": "energetic electronic music for coding",
            "spotify_id": "new_spotify_playlist_id_456", // May initially be null if creation is async
            "created_at": "2025-06-13T11:00:00Z",
            "spotify_url": "https://open.spotify.com/playlist/new_spotify_playlist_id_456"
        }
        ```
    *   This endpoint will:
        1.  Save the playlist to the local database.
        2.  Use `spotify_helpers` to create the playlist on Spotify.
        3.  Generate track recommendations based on `mood_prompt`.
        4.  Add tracks to the Spotify playlist.
        5.  Update the local playlist record with the `spotify_id`.
*   **`GET /api/playlists/{id}/`**: Retrieve a specific playlist.
    *   **Parameters**: `id` (integer, playlist ID)
    *   **Response (Success 200 OK)**: (Similar to single object in GET list)
*   **`PUT /api/playlists/{id}/`**: Update a specific playlist (primarily for non-Spotify fields like local description or mood prompt).
    *   **Parameters**: `id` (integer, playlist ID)
    *   **Request Body**: (Similar to POST, with fields to update)
*   **`PATCH /api/playlists/{id}/`**: Partially update a specific playlist.
    *   **Parameters**: `id` (integer, playlist ID)
    *   **Request Body**: (Similar to POST, with fields to update)
*   **`DELETE /api/playlists/{id}/`**: Delete a specific playlist (local record only by default; does not delete from Spotify unless explicitly implemented).
    *   **Parameters**: `id` (integer, playlist ID)
    *   **Response (Success 204 No Content)**

## Contributing

We welcome contributions to Filipy! If you'd like to help, please follow these guidelines:

1.  **Fork the Repository**: Create your own fork of the Filipy repository.
2.  **Clone Your Fork**:
    ```bash
    git clone https://github.com/MichalZak17/Filipy.git
    cd Filipy
    ```
3.  **Create a New Branch**:
    ```bash
    git checkout -b feature/your-descriptive-feature-name
    # or
    # git checkout -b bugfix/issue-tracker-id
    ```
4.  **Set Up Development Environment**: Follow the [Installation](#installation) steps (Docker or Virtual Environment).
5.  **Make Your Changes**: Implement your feature or bugfix.
6.  **Write Tests**: Add unit or integration tests for any new functionality or to cover bug fixes. Ensure all tests pass.
7.  **Lint Your Code**: (If a linter like Flake8 or Black is configured, run it).
8.  **Commit Your Changes**: Write clear and concise commit messages.
    ```bash
    git add .
    git commit -m "feat: Implement X feature" -m "Detailed description of changes."
    ```
9.  **Push to Your Fork**:
    ```bash
    git push origin feature/your-descriptive-feature-name
    ```
10. **Open a Pull Request (PR)**:
    *   Navigate to the original Filipy repository on GitHub.
    *   Click on "Pull Requests" and then "New Pull Request".
    *   Choose your fork and branch to compare with the main branch of the original repository.
    *   Provide a clear title and description for your PR, explaining the changes and referencing any related issues.

We'll review your PR as soon as possible. Thank you for contributing!

## Potential Future Enhancements

*   **Asynchronous Playlist Creation**: Utilize Celery (already a dependency) to offload Spotify API calls and playlist generation to background tasks for a non-blocking user experience.
*   **Advanced Mood Analysis**: Integrate NLP libraries (like Langchain, also a dependency) or AI services (OpenAI, Google GenAI - API key placeholders exist in `.env` example) for more sophisticated mood detection from user prompts.
*   **More Granular Playlist Customization**: Allow users to specify genres, artists to include/exclude, desired track count, playlist public/private status directly during creation.
*   **Enhanced Error Handling and User Feedback**: Improve frontend error display and provide more informative feedback during API interactions and playlist creation process.
*   **Expanded Testing**: Continue to expand unit and integration tests for both backend and frontend components.
*   **Playlist Editing/Updating**: Allow users to modify existing Filipy-created playlists (e.g., change mood prompt to regenerate tracks, add/remove tracks).
*   **Social Sharing**: Options to share created playlists.

## Changelog

A changelog will be maintained here or in a separate `CHANGELOG.md` file as the project evolves and new versions are released.

## License
This project is licensed under the [MIT License](LICENSE).

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Contact

For support, inquiries, or if you're interested in collaboration, please contact:
*   @MichalZak17 on GitHub