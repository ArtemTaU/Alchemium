from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from src.mixins import CreateMixin, ReadMixin, UpdateMixin

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    position = Column(String)

    profile = relationship("Profile", back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    bio = Column(String)

    user = relationship("User", back_populates="profile")


class UserRepository(CreateMixin, ReadMixin, UpdateMixin):
    model = User


class ProfileRepository(CreateMixin, ReadMixin):
    model = Profile


class DummyModel:
    def __init__(self, name=None, age=None):
        self.name = name
        self.age = age


class DummyRepository(UpdateMixin):
    model = DummyModel


class IncompleteRepository(UpdateMixin):
    model = None
