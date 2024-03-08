from sqladmin.authentication import AuthenticationBackend
from fastapi import Request


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        valid_usernames = ["admin"]
        valid_passwords = ["fQ8g5Kil3"]
        # Validate username/password credentials
        # And update session
        if username in valid_usernames and password in valid_passwords:
            request.session.update({"token": "..."})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        return True


