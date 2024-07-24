from social_core.backends.google import GoogleOAuth2

class pwGoogleOauth2(GoogleOAuth2):
    REDIRECT_STATE = False
    STATE_PARAMETER = False
