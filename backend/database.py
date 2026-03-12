import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base, User, Job
from typing import List, Optional, Dict
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=False  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(SessionLocal)

# For now, queries not filtered by user

def init_database():
    Base.metadata.create_all(bind=engine)

def get_session():
    return Session()

def close_session():
    Session.remove()

def get_all_jobs() -> List[Job]:
    session = get_session()
    try:
        return session.query(Job).all()
        # Here also we have to filter by user
    finally:
        session.close()

def get_job_by_whatever(field, target) -> List[Job]:
    session = get_session()
    try:
        if (field == "id"):
            return session.query(Job).filter(Job.id == target).first()
        elif (field == "site"):
            return session.query(Job).filter(Job.site == target).all()
        elif (field == "position"):
            return session.query(Job).filter(Job.position == target).all()
        elif (field == "location"):
            return session.query(Job).filter(Job.location == target).all()
        elif (field == "date_posted"):
            return session.query(Job).filter(Job.date_posted >= target).all()
        elif (field == "job_type"):
            return session.query(Job).filter(Job.job_type == target).all()
    finally:
        session.close()

def add_job(site: str, position: str, company: str, location: str, date_posted: datetime, **kwargs) -> Job:
    session = get_session()
    try:
        job = Job(
            site = site,
            position = position,
            company = company,
            location = location,
            date_posted = date_posted,
            job_url = kwargs.get('job_url'),
            job_url_direct = kwargs.get('jobs_url_direct'),
            job_type = kwargs.get('job_type'),
            description = kwargs.get('description'),
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        return job
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def remove_job(job_id: int) -> bool:
    session = get_session()
    try:
        job = session.query(Job).filter(Job.id == job_id).first()
        if job:
            session.delete(job)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()