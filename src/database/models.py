from sqlalchemy import Column, BIGINT, VARCHAR, TIMESTAMP, ForeignKey, SMALLINT, TEXT, BOOLEAN, INT
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "users"
    tg_id = Column(BIGINT, nullable=False, unique=True)
    username = Column(VARCHAR(64), nullable=True, unique=False)
    first_name = Column(VARCHAR(128), nullable=True, unique=False)
    last_name = Column(VARCHAR(128), nullable=True, unique=False)
    phone = Column(VARCHAR(16), nullable=True, unique=True)
    role_id = Column(SMALLINT, ForeignKey(column="role.id", ondelete="RESTRICT"), nullable=False, unique=False)
    date_sign_up = Column(TIMESTAMP, nullable=False, unique=False)
    is_male = Column(BOOLEAN, nullable=True, unique=False, default=None)
    note = Column(VARCHAR(128), nullable=True, unique=False)

    user_role = relationship(argument="Role", back_populates="users", lazy="joined")
    clubs = relationship(argument="UserClub", back_populates="user", lazy="joined")

    def __str__(self):
        if self.first_name and self.last_name:
            return self.first_name + " " + self.last_name
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        else:
            return self.tg_id

    def __repr__(self):
        return str(self)


class Role(Base):
    __tablename__ = "role"
    id = Column(SMALLINT, primary_key=True)
    name = Column(VARCHAR(16), nullable=False, unique=True)

    users = relationship(argument="User", back_populates="user_role")

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class Club(Base):
    __tablename__ = "club"
    name = Column(VARCHAR(64), nullable=False, unique=True)
    tag = Column(VARCHAR(16), nullable=False, unique=True)
    photo = Column(VARCHAR(512), nullable=True, unique=False)
    description = Column(TEXT, nullable=False, unique=False)

    users = relationship(argument="UserClub", back_populates="club", lazy="joined")

    def __str__(self):
        return self.tag

    def __repr__(self):
        return str(self)


class UserClub(Base):
    __tablename__ = "user_club"
    id = Column(BIGINT, primary_key=True)
    user_id = Column(BIGINT, ForeignKey(column="users.tg_id", ondelete="DELETE"), nullable=False, unique=False)
    club_id = Column(INT, ForeignKey(column="club.id", ondelete="CASCADE"), nullable=False, unique=False)

    user = relationship(argument="User", back_populates="clubs", lazy="joined")
    club = relationship(argument="Club", back_populates="users", lazy="joined")

    def __str__(self):
        return str(self.user) + " " + str(self.club)

    def __repr__(self):
        return str(self)
