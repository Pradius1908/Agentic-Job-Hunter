import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from typing import Optional, List
import csv
from jobspy import scrape_jobs
from langchain_core.messages import SystemMessage

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI (
    model = "gemini-2.5-flash", google_api_key = GEMINI_API_KEY
)

dumb_llm = ChatGoogleGenerativeAI (
    model = "gemini-2.5-flash", google_api_key = GEMINI_API_KEY
)

chat_history = [SystemMessage(content = "You are an AI assistant that helps people look for jobs.")]

class JobsInfo(BaseModel):
    site: Optional[List[str]] = Field(description="The job site to search for jobs on")
    search_term: str = Field(description="The post for which to search for jobs")
    google_search_term: str = Field(description="A string that contains post, location and time, used to search on Google Jobs")
    location: Optional[str] = Field(description="The location to search for jobs in")
    results_wanted: Optional[int] = Field(description="The number of results to return")
    hours_old: Optional[int] = Field(description="The number of hours to search for jobs in the past")
    country_indeed: Optional[str] = Field(description="The country to search for jobs in")

def make_agent():
    agent = create_agent(
        model=llm,
        response_format=JobsInfo  # Auto-selects ProviderStrategy
    )
    return agent

SYSTEM_PROMPT = """You are a job search agent that should summarise job details in a 4-6 sentences. Mention all important information about the job."""

def make_dumb_agent():
    agent = create_agent(
        model=dumb_llm,
        system_prompt = SYSTEM_PROMPT
    )
    return agent

def refine_result(result):
    if result.site == None:
        site_name = ["indeed", "linkedin", "zip_recruiter", "google", "glassdoor", "bayt", "naukri"]
    else:
        site_name = result.site

    if result.search_term == None:
        search_term = "engineer"
    else:
        search_term = result.search_term

    if result.google_search_term == None:
        google_search_term = "engineer jobs in San Francisco, since yesterday"
    else:
        google_search_term = result.google_search_term

    if result.location == None:
        location = "Bengaluru, Karnataka"
    else:
        location = result.location

    if result.hours_old == None:
        hours_old = 72
    else:
        hours_old = result.hours_old

    if result.results_wanted == None:
        results_wanted = 1
    else:
        results_wanted = result.results_wanted

    if result.country_indeed == None:
        country_indeed = "India"
    else:
        country_indeed = result.country_indeed
    
    return site_name, search_term, google_search_term, location, hours_old, results_wanted, country_indeed

def get_jobs(site_name, search_term, google_search_term, location, results_wanted, hours_old, country_indeed):
    jobs = scrape_jobs(
        site_name=site_name,
        search_term=search_term,
        google_search_term=google_search_term,
        location=location,
        results_wanted=results_wanted,
        hours_old=hours_old,
        country_indeed=country_indeed,

        # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
        # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
    )
    print(f"Found {len(jobs)} jobs")
    #print(jobs.head())
    print(jobs)
    jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_excel