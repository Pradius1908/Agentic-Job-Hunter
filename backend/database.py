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
#considering user management functions 
#retrieving user by email address
def get_user_email(email: str) -> Optional[User]:
    session = get_session()
    try:
        return session.query(User).filter(User.email == email).first()
    finally:        session.close()

def create_or_update_user(email:str,name:str, extracted_skills: str=None) -> User:
    session = get_session()
    try:
        user = session.query(User).filter(User.email == email).first()
        if user:
            if extracted_skills:
                user.skills = extracted_skills
        else:
            user = User(email=email, name=name, skills=extracted_skills)
            session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()
#aady edit-1 for users ends here
 
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
        #aady edit-2 for preventing duplicate jobs from being added
        existing_job = session.query(Job).filter(
            Job.job_url == kwargs.get('job_url')
        ).first()
        if existing_job:
            return existing_job
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
def save_jobs_in_bulk(jobs_data: List[dict]):
    session = get_session()
    try:
        new_jobs=[]
        for job_dict in jobs_data:
            if not session.query(Job).filter(Job.job_url == job_dict.get('job_url')).first():
                job= Job(
                    site=job_dict.get('site','unknown'),
                    position=job_dict.get('title',''),
                    company=job_dict.get('company',''),
                    location=job_dict.get('location',''),
                    job_url=job_dict.get('job_url',''),
                    date_posted=datetime.utcnow(),
                )
                new_jobs.append(job)
        if new_jobs:
            session.bulk_save_objects(new_jobs)
            session.commit()
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