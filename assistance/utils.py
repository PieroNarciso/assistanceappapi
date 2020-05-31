from rest_framework.authtoken.models import Token


class UserHandler(object):

    def get_login_data(self, user):
        """Return dictionary with user data. User parameter is an 
        User instance object"""
        token, created = Token.objects.get_or_create(user=user)
        result = self.get_token_data(user, token)
        return result

    def get_token_data(self, user, token):
        result = self.get_user_data(user)
        result['token'] = token.key
        return result

    def get_user_data(self, user):
        result = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "login": True,
            "is_staff": user.is_staff
        }
        return result
