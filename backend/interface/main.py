import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Body, Cookie, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from result import Err, Ok
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

from backend.application.auth_service import AuthService
from backend.config import CONFIG
from backend.infrastructure.email_sender import BrevoEmailSender
from backend.infrastructure.rq_client import RQClient
from backend.infrastructure.user_repository import MongoUserRepository

app = FastAPI()

# Initialize RQ client for job management
rq_client = RQClient()
auth_service = AuthService(
    repository=MongoUserRepository(CONFIG.mongo_uri, CONFIG.mongo_db_name),
    email_sender=BrevoEmailSender(),
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware (required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
)

# OAuth configuration
config = Config(
    environ={
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id"),
        "GOOGLE_CLIENT_SECRET": os.getenv(
            "GOOGLE_CLIENT_SECRET", "your-google-client-secret"
        ),
        "FACEBOOK_CLIENT_ID": os.getenv(
            "FACEBOOK_CLIENT_ID", "your-facebook-client-id"
        ),
        "FACEBOOK_CLIENT_SECRET": os.getenv(
            "FACEBOOK_CLIENT_SECRET", "your-facebook-client-secret"
        ),
        "TWITTER_CLIENT_ID": os.getenv("TWITTER_CLIENT_ID", "your-twitter-client-id"),
        "TWITTER_CLIENT_SECRET": os.getenv(
            "TWITTER_CLIENT_SECRET", "your-twitter-client-secret"
        ),
    }
)

oauth = OAuth(config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="facebook",
    client_id=config("FACEBOOK_CLIENT_ID"),
    client_secret=config("FACEBOOK_CLIENT_SECRET"),
    access_token_url="https://graph.facebook.com/oauth/access_token",
    authorize_url="https://www.facebook.com/dialog/oauth",
    api_base_url="https://graph.facebook.com/",
    client_kwargs={"scope": "email public_profile"},
)

oauth.register(
    name="twitter",
    client_id=config("TWITTER_CLIENT_ID"),
    client_secret=config("TWITTER_CLIENT_SECRET"),
    authorize_url="https://twitter.com/i/oauth2/authorize",
    access_token_url="https://api.twitter.com/2/oauth2/token",
    api_base_url="https://api.twitter.com/2/",
    client_kwargs={
        "scope": "tweet.read users.read offline.access",
        # Changed from client_secret_post
        "token_endpoint_auth_method": "client_secret_basic",
        "code_challenge_method": "S256",  # PKCE required by Twitter OAuth 2.0
    },
)

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"


def create_access_token(subject: str, expires_delta: timedelta) -> str:
    """Create a JWT access token"""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": subject, "exp": expire,
                 "iat": datetime.now(timezone.utc)}
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
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def _convert_expires_at(token: dict[str, object]) -> datetime | None:
    expires_at_raw = token.get("expires_at")
    if isinstance(expires_at_raw, (int, float)):
        return datetime.fromtimestamp(expires_at_raw, timezone.utc)
    return None


def _build_login_response(user_id: str) -> RedirectResponse:
    """Create a cookie-based redirect response for authenticated users."""
    access_token = create_access_token(
        subject=user_id,
        expires_delta=timedelta(minutes=15),
    )

    response = RedirectResponse(url=CONFIG.frontend_url)
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


@app.post("/auth/register")
def register_user(payload: dict = Body(...)) -> dict[str, str]:
    match auth_service.register_user(payload.get("email", ""), payload.get("password", "")):
        case Ok(identifier):
            return {"user_id": identifier, "status": "pending_validation"}
        case Err(error):
            raise HTTPException(status_code=400, detail=error)


@app.post("/auth/login")
def login_user(payload: dict = Body(...)) -> RedirectResponse:
    match auth_service.authenticate(payload.get("email", ""), payload.get("password", "")):
        case Ok(user):
            if user.identifier is None:
                raise HTTPException(status_code=400, detail="User identifier missing")
            return _build_login_response(user.identifier)
        case Err(error):
            raise HTTPException(status_code=400, detail=error)


@app.get("/validate")
def validate_account(token: str) -> RedirectResponse:
    match auth_service.validate_account(token):
        case Ok(_):
            response = RedirectResponse(url=CONFIG.frontend_url)
            response.set_cookie(
                key="validation_status",
                value="validated",
                max_age=300,
            )
            return response
        case Err(error):
            raise HTTPException(status_code=400, detail=error)


@app.get("/auth/google")
async def auth_google(request: Request):
    """Initialize OAuth flow with Google"""
    redirect_uri = os.getenv(
        "REDIRECT_URI", "http://localhost:8000/auth/google/callback"
    )
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google/callback")
async def google_callback(request: Request):
    """
    Handle Google OAuth callback
    Exchange code for token, create/find user, and redirect to frontend with cookie
    """
    # 1. Exchange 'code' with Google to get user info
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        return {"error": "Failed to get user info"}

    provider_user_id = user_info.get("sub", "")
    match auth_service.register_oauth_user(
        "google",
        str(provider_user_id),
        user_info.get("email"),
        token.get("access_token"),
        token.get("refresh_token"),
        _convert_expires_at(token),
    ):
        case Ok(identifier):
            return _build_login_response(identifier)
        case Err(error):
            raise HTTPException(status_code=400, detail=error)


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
    resp = await oauth.facebook.get("me?fields=id,name,email", token=token)
    user_info = resp.json()

    if not user_info:
        return {"error": "Failed to get user info"}

    user_id = user_info.get("id", "")

    match auth_service.register_oauth_user(
        "facebook",
        str(user_id),
        user_info.get("email"),
        token.get("access_token"),
        token.get("refresh_token"),
        _convert_expires_at(token),
    ):
        case Ok(identifier):
            return _build_login_response(identifier)
        case Err(error):
            raise HTTPException(status_code=400, detail=error)


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
    resp = await oauth.twitter.get("users/me", token=token)
    user_info = resp.json().get("data", {})

    if not user_info:
        return {"error": "Failed to get user info"}

    user_id = user_info.get("id", "")

    match auth_service.register_oauth_user(
        "twitter",
        str(user_id),
        None,
        token.get("access_token"),
        token.get("refresh_token"),
        _convert_expires_at(token),
    ):
        case Ok(identifier):
            return _build_login_response(identifier)
        case Err(error):
            raise HTTPException(status_code=400, detail=error)


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
    except jwt.PyJWTError:
        return {"error": "Invalid token"}


# ============================================================================
# Job Management API Endpoints
# ============================================================================


@app.post("/jobs/start")
def start_job(
    total_items: int = 100,
    access_token: Optional[str] = Cookie(None),
) -> dict[str, str]:
    """Start a new long-running job.

    Args:
        total_items: Number of items to process (default: 100)
        access_token: JWT access token from cookie

    Returns:
        Dictionary with job_id or error message
    """
    verify_token(access_token)

    from result import Err, Ok

    result = rq_client.enqueue_job(
        "backend.application.commands_async.example_long_task.execute_example_long_task_job",
        total_items,
        job_timeout=7200,
    )

    match result:
        case Ok(job_id):
            return {"job_id": job_id, "status": "started"}
        case Err(error):
            raise HTTPException(status_code=500, detail=str(error))


@app.get("/jobs/{job_id}/status")
def get_job_status(
    job_id: str,
    access_token: Optional[str] = Cookie(None),
) -> dict[str, str]:
    """Get the status of a job.

    Args:
        job_id: The job ID to check
        access_token: JWT access token from cookie

    Returns:
        Dictionary with job status
    """
    verify_token(access_token)

    from result import Err, Ok

    result = rq_client.get_job_status(job_id)

    match result:
        case Ok(status):
            return {"job_id": job_id, "status": status}
        case Err(error):
            raise HTTPException(status_code=404, detail=str(error))


@app.get("/jobs/{job_id}/meta")
def get_job_meta(
    job_id: str,
    access_token: Optional[str] = Cookie(None),
) -> dict[str, object]:
    """Get the metadata of a job.

    Args:
        job_id: The job ID to get metadata for
        access_token: JWT access token from cookie

    Returns:
        Dictionary with job metadata
    """
    verify_token(access_token)

    from result import Err, Ok

    result = rq_client.get_job_meta(job_id)

    match result:
        case Ok(metadata):
            return {"job_id": job_id, "metadata": metadata}
        case Err(error):
            raise HTTPException(status_code=404, detail=str(error))


@app.post("/jobs/{job_id}/cancel")
def cancel_job(
    job_id: str,
    access_token: Optional[str] = Cookie(None),
) -> dict[str, str]:
    """Cancel a running or queued job.

    Args:
        job_id: The job ID to cancel
        access_token: JWT access token from cookie

    Returns:
        Dictionary with cancellation status
    """
    verify_token(access_token)

    from result import Err, Ok

    result = rq_client.cancel_job(job_id)

    match result:
        case Ok(_):
            return {"job_id": job_id, "status": "canceled"}
        case Err(error):
            raise HTTPException(status_code=500, detail=str(error))
