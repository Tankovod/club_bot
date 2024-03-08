from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from src.database.models import Base
from .model_views import UserAdmin, UserClubAdmin, RoleAdmin, ClubAdmin
from .auth import AdminAuth


app = FastAPI(
    title="Club-Admin"
)

app.add_middleware(CORSMiddleware,
                   **{'allow_methods': ('*',), 'allow_origins': ('*',),
                      'allow_headers': ('*',), 'allow_credentials': True})

authentication_backend = AdminAuth(secret_key="...")
admin = Admin(app=app, authentication_backend=authentication_backend, engine=Base.async_engine)
admin.add_view(UserAdmin)
admin.add_view(ClubAdmin)
admin.add_view(UserClubAdmin)
admin.add_view(RoleAdmin)


if __name__ == "__main__":
    from uvicorn import run

    run(
        app=app,
        host="0.0.0.0",
        port=8000
    )
