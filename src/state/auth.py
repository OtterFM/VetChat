import reflex as rx
import secrets
from datetime import datetime, timedelta
from ..models import User, AuthSession, verify_password, hash_token, verify_token


class AuthState(rx.State):
    """Authentication sub-state - handles login, logout, session management"""

    session_token: str = rx.LocalStorage("")
    current_user: User | None = None
    username: str = ""
    password: str = ""
    error_message: str = ""

    @rx.var
    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def set_username(self, value: str):
        self.username = value

    def set_password(self, value: str):
        self.password = value

    def check_login(self):
        """Run this on every page load to validate the token"""
        if not self.session_token:
            return rx.redirect("/")

        with rx.session() as session:
            # Get all sessions for this user to check against
            auth_sessions = session.exec(
                AuthSession.select().where(
                    AuthSession.expires_at > datetime.utcnow()
                )
            ).all()

            # Find matching session by verifying token hash
            valid_session = None
            for auth_session in auth_sessions:
                try:
                    if verify_token(self.session_token, auth_session.token):
                        valid_session = auth_session
                        break
                except ValueError:
                    # Invalid bcrypt hash in database, skip this session
                    continue

            if valid_session:
                self.current_user = session.get(User, valid_session.user_id)
            else:
                # Token invalid/expired -> redirect to login
                self.current_user = None
                return rx.redirect("/")

    def logout(self):
        if not self.session_token:
            return rx.redirect("/")

        with rx.session() as session:
            # Find and delete the matching session by verifying token hash
            auth_sessions = session.exec(
                AuthSession.select()
            ).all()

            for auth_session in auth_sessions:
                try:
                    if verify_token(self.session_token, auth_session.token):
                        session.delete(auth_session)
                        session.commit()
                        break
                except ValueError:
                    # Invalid bcrypt hash in database, skip this session
                    continue

            self.session_token = ""
            self.current_user = None

            return rx.redirect("/")

    def login(self):

        with rx.session() as session:
            # Clean up expired sessions
            now = datetime.utcnow()
            expired = session.exec(
                AuthSession.select().where(AuthSession.expires_at < now)
            ).all()
            for old_session in expired:
                session.delete(old_session)
            if expired:
                session.commit()

            user = session.exec(
                User.select().where(User.username == self.username)
            ).first()

            if not user:
                self.error_message = "Invalid credentials"
                return

            if user.locked_until and datetime.utcnow() < user.locked_until:
                wait_time = user.locked_until - datetime.utcnow()
                minutes_left = int(wait_time.total_seconds() / 60) + 1
                self.error_message = f"Too many attempts. Try again in {minutes_left} minutes."
                return

            if verify_password(self.password, user.password_hash):
                user.failed_attempts = 0
                user.locked_until = None
                session.add(user)

                new_token = secrets.token_urlsafe(32)
                hashed_token = hash_token(new_token)
                expiration = datetime.utcnow() + timedelta(hours=2)

                new_session = AuthSession(
                    user_id=user.id,
                    token=hashed_token,
                    expires_at=expiration
                )
                session.add(new_session)
                session.commit()

                self.session_token = new_token  # Store plain token in client
                self.error_message = ""
                return rx.redirect("/chat")

            else:  # 5 failed attempts allowed. 5 mins waiting time.
                user.failed_attempts += 1
                if user.failed_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=5)
                    user.failed_attempts = 0
                    session.add(user)
                    session.commit()
                    self.error_message = "Too many attempts. Try again in 5 minutes."
                else:
                    session.add(user)
                    session.commit()
                    self.error_message = "Invalid credentials"
