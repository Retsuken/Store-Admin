from django.contrib.auth.backends import ModelBackend
from .models import Team, User  # Импортируйте User и Team
from .forms import LoginForm


class TeamBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, *kwargs):
        try:
            # Поиск пользователя в модели User по полю name (если у вас есть такое поле)
            user = User.objects.get(name=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            try:
                # Поиск пользователя в модели Team по полю login
                team = Team.objects.get(login=username)
                if team.check_password(password):
                    return team
            except Team.DoesNotExist:
                return None

    def get_user(self, user_id):
        try:
            # Поиск пользователя в модели User по ID
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            try:
                # Поиск пользователя в модели Team по ID
                return Team.objects.get(pk=user_id)
            except Team.DoesNotExist:
                return None