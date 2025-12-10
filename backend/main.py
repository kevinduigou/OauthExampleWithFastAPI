from fastapi import FastAPI, Response, Request, Cookie, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from datetime import timedelta, timezone
import os
from typing import Optional
import jwt
from datetime import datetime

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware (required for OAuth)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"))

# OAuth configuration
config = Config(environ={
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret"),
    "FACEBOOK_CLIENT_ID": os.getenv("FACEBOOK_CLIENT_ID", "your-facebook-client-id"),
    "FACEBOOK_CLIENT_SECRET": os.getenv("FACEBOOK_CLIENT_SECRET", "your-facebook-client-secret"),
    "TWITTER_CLIENT_ID": os.getenv("TWITTER_CLIENT_ID", "your-twitter-client-id"),
    "TWITTER_CLIENT_SECRET": os.getenv("TWITTER_CLIENT_SECRET", "your-twitter-client-secret"),
})

oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

oauth.register(
    name='facebook',
    client_id=config('FACEBOOK_CLIENT_ID'),
    client_secret=config('FACEBOOK_CLIENT_SECRET'),
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    api_base_url='https://graph.facebook.com/',
    client_kwargs={
        'scope': 'email public_profile'
    }
)

oauth.register(
    name='twitter',
    client_id=config('TWITTER_CLIENT_ID'),
    client_secret=config('TWITTER_CLIENT_SECRET'),
    authorize_url='https://twitter.com/i/oauth2/authorize',
    access_token_url='https://api.twitter.com/2/oauth2/token',
    api_base_url='https://api.twitter.com/2/',
    client_kwargs={
        'scope': 'tweet.read users.read offline.access',
        'token_endpoint_auth_method': 'client_secret_basic',  # Changed from client_secret_post
        'code_challenge_method': 'S256'  # PKCE required by Twitter OAuth 2.0
    }
)

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"


def create_access_token(subject: str, expires_delta: timedelta) -> str:
    """Create a JWT access token"""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(access_token: Optional[str]) -> dict:
    """Verify JWT token and return payload"""
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def _build_login_response(user_id: str) -> RedirectResponse:
    """Create a cookie-based redirect response for authenticated users."""
    access_token = create_access_token(
        subject=user_id,
        expires_delta=timedelta(minutes=15),
    )

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000/app")
    response = RedirectResponse(url=frontend_url)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=15 * 60,
    )
    return response


@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "OAuth Example API"}


@app.get("/auth/google")
async def auth_google(request: Request):
    """Initialize OAuth flow with Google"""
    redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google/callback")
async def google_callback(request: Request):
    """
    Handle Google OAuth callback
    Exchange code for token, create/find user, and redirect to frontend with cookie
    """
    # 1. Exchange 'code' with Google to get user info
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo')

    if not user_info:
        return {"error": "Failed to get user info"}
    
    # 2. Find/create user in DB, get user_id
    # For this example, we'll use the Google user ID
    user_id = user_info.get('sub')  # Google's unique user ID

    return _build_login_response(user_id)


@app.get("/auth/facebook")
async def auth_facebook(request: Request):
    """Initialize OAuth flow with Facebook"""
    redirect_uri = os.getenv(
        "FACEBOOK_REDIRECT_URI", "http://localhost:8000/auth/facebook/callback"
    )
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


@app.get("/auth/facebook/callback")
async def facebook_callback(request: Request):
    """Handle Facebook OAuth callback and issue local token."""
    token = await oauth.facebook.authorize_access_token(request)
    resp = await oauth.facebook.get('me?fields=id,name,email', token=token)
    user_info = resp.json()

    if not user_info:
        return {"error": "Failed to get user info"}

    user_id = user_info.get('id')

    return _build_login_response(user_id)


@app.get("/auth/twitter")
async def auth_twitter(request: Request):
    """Initialize OAuth flow with Twitter"""
    redirect_uri = os.getenv(
        "TWITTER_REDIRECT_URI", "http://localhost:8000/auth/twitter/callback"
    )
    return await oauth.twitter.authorize_redirect(request, redirect_uri)


@app.get("/auth/twitter/callback")
async def twitter_callback(request: Request):
    """Handle Twitter OAuth callback and issue local token."""
    token = await oauth.twitter.authorize_access_token(request)
    resp = await oauth.twitter.get('users/me', token=token)
    user_info = resp.json().get('data', {})

    if not user_info:
        return {"error": "Failed to get user info"}

    user_id = user_info.get('id')

    return _build_login_response(user_id)


@app.get("/auth/me")
def get_current_user(access_token: Optional[str] = None):
    """
    Get current user from JWT token
    In a real app, you'd extract the token from the cookie
    """
    if not access_token:
        return {"error": "Not authenticated"}
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return {"user_id": user_id, "authenticated": True}
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.JWTError:
        return {"error": "Invalid token"}


@app.get("/movies")
def get_best_movies(access_token: Optional[str] = Cookie(None)):
    """
    Get list of best movies ever - requires authentication
    """
    # Verify the user is authenticated
    payload = verify_token(access_token)
    
    # Return the list of best movies
    movies = [
        {"id": 1, "title": "Coherence", "year": 2013, "director": "James Ward Byrkit"},
        # Brilliant low-budget sci-fi mind-bender built entirely on improvisation.

        {"id": 2, "title": "Timecrimes (Los Cronocrímenes)", "year": 2007, "director": "Nacho Vigalondo"},
        # Tight, original time-travel thriller with zero fat.

        {"id": 3, "title": "The Man From Earth", "year": 2007, "director": "Richard Schenkman"},
        # Pure dialogue film exploring immortality and philosophy.

        {"id": 4, "title": "The Fall", "year": 2006, "director": "Tarsem Singh"},
        # Visually extraordinary fantasy drama shot in 20+ countries.

        {"id": 5, "title": "Upgrade", "year": 2018, "director": "Leigh Whannell"},
        # Extremely well-executed sci-fi action with a sharp script.

        {"id": 6, "title": "A Ghost Story", "year": 2017, "director": "David Lowery"},
        # Meditation on time and grief with a unique style.

        {"id": 7, "title": "The Proposition", "year": 2005, "director": "John Hillcoat"},
        # Brutal, poetic Australian western written by Nick Cave.

        {"id": 8, "title": "In Bruges", "year": 2008, "director": "Martin McDonagh"},
        # Dark comedy crime film with perfect writing.

        {"id": 9, "title": "Enemy", "year": 2013, "director": "Denis Villeneuve"},
        # Surreal psychological thriller—intense, ambiguous, unforgettable.

        {"id": 10, "title": "The Handmaiden", "year": 2016, "director": "Park Chan-wook"},
        # Exquisite Korean thriller full of twists and visual mastery.

        {"id": 11, "title": "The Wailing", "year": 2016, "director": "Na Hong-jin"},
        # Criminally underrated horror-thriller with massive craft.

        {"id": 12, "title": "Victoria", "year": 2015, "director": "Sebastian Schipper"},
        # Entire film shot in a single continuous take—remarkable tension.

        {"id": 13, "title": "Columbus", "year": 2017, "director": "Kogonada"},
        # Quiet, elegant drama with stunning architecture cinematography.

        {"id": 14, "title": "Sound of Noise", "year": 2010, "director": "Ola Simonsson & Johannes Stjärne Nilsson"},
        # Wild Swedish comedy about anarchist musicians.

        {"id": 15, "title": "The Invitation", "year": 2015, "director": "Karyn Kusama"},
        # Slow-burn psychological thriller with a killer payoff.
    ]
    
    return {"movies": movies, "user_id": payload.get("sub")}
