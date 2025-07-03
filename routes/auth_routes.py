from flask import Blueprint, redirect, session, url_for, request
import google_auth_oauthlib.flow
import os
from google.oauth2.credentials import Credentials
import google_auth_oauthlib.flow

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '0'  # only in development mode

auth_bp = Blueprint('auth', __name__)

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/drive'
]

@auth_bp.route('/authorize')
def authorize():
    session.clear()  # 🧼 Clears old credentials and state

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        os.environ["GOOGLE_CLIENT_SECRET_FILE"], SCOPES)
    flow.redirect_uri = url_for('auth.oauth2callback', _external=True)

    auth_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )

    session['state'] = state
    return redirect(auth_url)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(os.environ.get("FRONTEND_URL"))  # or to your login screen


@auth_bp.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    if not state:
        return "Missing state in session", 400

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        os.environ["GOOGLE_CLIENT_SECRET_FILE"],
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = url_for('auth.oauth2callback', _external=True)

    # Finalize the flow and get credentials
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    # Store full credential info in session
    session['credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    return redirect(f"{os.environ.get('FRONTEND_URL')}/dashboard?drive_connected=1")