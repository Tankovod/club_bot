from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from src.database.models import Base
from .model_views import UserAdmin, UserClubAdmin, RoleAdmin, ClubAdmin


app = FastAPI(
    title="Club-Admin"
)

app.add_middleware(CORSMiddleware,
                   **{'allow_methods': ('*',), 'allow_origins': ('*',),
                      'allow_headers': ('*',), 'allow_credentials': True})

admin = Admin(app=app, engine=Base.async_engine)
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
