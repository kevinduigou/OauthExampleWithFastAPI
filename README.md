# OauthExampleWithFastAPI

Sample FastAPI + React application demonstrating OAuth logins with Google, Facebook, and Twitter. Update the following environment variables (e.g., in a `.env` file) to use your own credentials:

- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `FACEBOOK_CLIENT_ID` / `FACEBOOK_CLIENT_SECRET`
- `TWITTER_CLIENT_ID` / `TWITTER_CLIENT_SECRET`
- `REDIRECT_URI`, `FACEBOOK_REDIRECT_URI`, `TWITTER_REDIRECT_URI` (optional overrides for callback URLs)
- `FRONTEND_URL` (defaults to `http://localhost:3000/app`)

Start the FastAPI backend at port `8000` and the React frontend at port `3000`. Use the buttons on the home page to initiate the OAuth flow with your preferred provider.
