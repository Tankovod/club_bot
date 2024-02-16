from sqladmin import ModelView
from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from src.database.models import User, Club, Role, UserClub


class UserAdmin(ModelView, model=User):
    column_list = ["username", "first_name", "last_name", "date_sign_up"]
    name = "Пользователь"
    name_plural = "Пользователи"


class ClubAdmin(ModelView, model=Club):
    column_list = ["name", "description"]
    name = "Клуб"
    name_plural = "Клубы"


class RoleAdmin(ModelView, model=Role):
    column_list = ["name"]
    name = "Группа"
    name_plural = "Группы"
    can_edit = False
    can_delete = False


class UserClubAdmin(ModelView, model=UserClub):
    column_list = ["user", "club"]
    name = "Клуб пользователя"
    name_plural = "Клубы пользователей"