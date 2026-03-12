from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime

class Base (DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    #jobs_searched = relationship("Job", back_populates="user", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    #user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    site = Column(String(255), nullable=False)
    job_url = Column(String(255))
    job_url_direct = Column(String(255))
    position = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    date_posted = Column(DateTime, nullable=False)
    job_type = Column(String(255))
    description = Column(String)
    #user = relationship("User", back_populates="jobs_searched")