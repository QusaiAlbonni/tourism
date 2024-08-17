# MIT License
# 
# Copyright (c) 2020 Walison Filipe
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
import jwt
from firebase_admin import auth, credentials, initialize_app, app_check

from django.conf import settings

from firebase_auth.settings import firebase_auth_settings


User = get_user_model()

firebase = settings.FIREBASE_APP

class BaseFirebaseAuthentication(BaseAuthentication):
    """
    Base implementation of token based authentication using firebase.
    """

    www_authenticate_realm = "api"
    auth_header_prefix = "JWT"
    uid_field = User.USERNAME_FIELD

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and decoded firebase payload if a valid signature
        has been supplied. Otherwise returns `None`.
        """
        firebase_token = self.get_token(request)
        

        if not firebase_token:
            return None

        try:
            payload = auth.verify_id_token(firebase_token, firebase)
        except ValueError as e:
            msg = _("Invalid firebase ID token.")
            return None
        except (
            auth.ExpiredIdTokenError,
            auth.InvalidIdTokenError,
            auth.RevokedIdTokenError,
        ) as e:
            try:
                payload = jwt.decode(firebase_token, options={"verify_signature": False})
            except jwt.ExpiredSignatureError:
                print("The token has expired")
                return None
            except jwt.InvalidTokenError:
                print("Invalid token")
                return None            
            msg = _("Could not log in.")
        try: 
            user = self.authenticate_credentials(payload)
        except Exception as e:
            return None
        
        return (user, payload)

    def get_token(self, request):
        """
        Returns the firebase ID token from request.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.auth_header_prefix.lower().encode():
            return None

        if len(auth) == 1:
            msg = _("Invalid Authorization header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _(
                "Invalid Authorization header. Token string should not contain spaces."
            )
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_credentials(self, payload):
        """
        Returns an user that matches the payload's user uid and email.
        """
        if payload["firebase"]["sign_in_provider"] == "anonymous":
            msg = _("Firebase anonymous sign-in is not supported.")
            raise exceptions.AuthenticationFailed(msg)

        if firebase_auth_settings.EMAIL_VERIFICATION:
            if not payload["email_verified"]:
                msg = _("User email not yet confirmed.")
                raise exceptions.AuthenticationFailed(msg)
        uid = payload["user_id"]
        email = payload['email']
        name = payload['name']
        try:
            print('das')
            user = self.get_user(email)
        except User.DoesNotExist:
            firebase_user = auth.get_user(uid)
            print(name)
            try:
                user = self.create_user_from_firebase(name, email, firebase_user)
            except Exception as e:
                print(e)
        return user

    def get_user(self, email: str) -> User:
        return User.objects.get(email=email)
    
    def create_user_from_firebase(
        self, username, email: str, firebase_user: auth.UserRecord
    ) -> User:
        print('das')
        parts = username.split()
        if len(parts) == 1:
            first_name = parts[0]
            second_name = ''
        elif len(parts) > 1:
            first_name = parts[0]
            second_name = ' '.join(parts[1:]) 
        user = User(email= email, username= first_name, first_name= first_name, second_name=second_name)
        user.set_unusable_password()
        user.save()
        profile = user.profile
        profile.avatar = firebase_user.photo_url
        profile.save()
        return user
        
        
    def authenticate_header(self, request):
        return '{} realm="{}"'.format(
            self.auth_header_prefix, self.www_authenticate_realm
        )


class FirebaseAuthentication(BaseFirebaseAuthentication):
    """
    Token based authentication using firebase.

    Clients should authenticate by passing a Firebase ID token in the
    Authorizaiton header using Bearer scheme.
    """

    def get_user(self, email: str) -> User:
        return User.objects.get(email=email)
    
    def create_user_from_firebase(
        self, username, email: str, firebase_user: auth.UserRecord
    ) -> User:
        print('das')
        parts = username.split()
        if len(parts) == 1:
            first_name = parts[0]
            second_name = ''
        elif len(parts) > 1:
            first_name = parts[0]
            second_name = ' '.join(parts[1:]) 
        user = User(email= email, username= first_name, first_name= first_name, last_name=second_name)
        user.set_unusable_password()
        user.save()
        return user
