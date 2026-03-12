import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from JobspyFuncs import make_agent, make_dumb_agent, refine_result, get_jobs, chat_history, dumb_llm
from ApifyFuncs import client, indeedToJSON, naukriToJSON
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from math import ceil
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from JobspyFuncs import JobsInfo, SearchFields

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

chat_history = [SystemMessage(content = "You are an AI assistant that helps people look for jobs.")]

"""
llm = ChatGoogleGenerativeAI (
    model = "gemini-2.5-flash", google_api_key = GEMINI_API_KEY
)
"""

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=GROQ_API_KEY,
)

class MessageClassifier(BaseModel):
    message_type: Literal["getjobs", "help"] = Field(
        ...,
        description="Classify if the message requires to fetch more jobs or provide additional help."
    )

class YesNoClassifier(BaseModel):
    message_type: Literal["yes", "no"] = Field(
        ...,
        description="Classify if the user wants to go ahead with the job search with the existing parameters or not."
    )

class HelpClassifier(BaseModel):
    message_type: Literal["general", "database"] = Field(
        ...,
        description="Classify if the user has a general query or a query about previously searched jobs."
    )

class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None

def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)
    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
                        - 'getjobs': if it asks to search for jobs related to specific positions, locations, websites or other details
                        - 'help': if it asks for information or opinions"""
        },
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}

def router(state: State):
    message_type = state.get("message_type", "help")
    if message_type == "getjobs":
        return {"next": "getjobs"}
    return {"next": "help"}

def getjobs_agent(state: State):
    last_message = state["messages"][-1]
    messages = [
        {"role": "system",
         "content": """You are an agent that determines what kind of jobs the user wants to search for.
                        Look for key factors about the job that the user wants, like position title, job search companies, location and more.
                        The default values in case of unspecified information are: post: engineer, location: Bengaluru(Karnataka, India), number of results wanted: 1, number of hours old: 72.
                        Reiterate the important details about the user's request and mention default values in case of unspecified information.
                        If any important details like the post or location is vague, illegitimate or missing, ask the user if they want to specify more clearly.
                        Ask if they want to specify more details, or if they want to go ahead and search for jobs with the existing details."""
        },
        {
            "role": "user",
            "content": str(chat_history)
        }
    ]
    reply = llm.invoke(messages)
    chat_history.append(AIMessage(content = reply.content))
    print(reply.content)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

def yes_or_no(state: State):
    user_input = input("Yes or no Message: ")
    if user_input == "exit":
            print("Bye")
            exit()
    chat_history.append(HumanMessage(content = user_input))
    state["messages"].append(HumanMessage(content = user_input))
    last_message = state["messages"][-1]
    yes_no_classifier_llm = llm.with_structured_output(YesNoClassifier)
    result = yes_no_classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
                        - 'yes': if the user gives a wants to go ahead with the current details and does not want to change anything.
                        - 'no': if the user wants something different, is unsure or or wants to specify more details."""
        },
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}

def job_router(state: State):
    message_type = state.get("message_type", "no")
    if message_type == "yes":
        return {"next": "scrape"}
    return {"next": "end"}

def classify_help(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(HelpClassifier)
    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
                        - 'general': if the user is asking for general details or opinions that do not need previously searched job data
                        - 'help': if the user is asking about previously searched job data"""
        },
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}

def help_router(state: State):
    message_type = state.get("message_type", "general")
    if message_type == "database":
        return {"next": "database"}
    return {"next": "general"}

def help_agent(state: State):
    messages = [
        {"role": "system",
         "content": """You are an agent who answers general questions related to jobs.
                        If you are required to give an opinion, provide clear, concise opinions based on evidence.
                        Do not tell the user to follow any specific career path, but you can mention the best options for them.
                        If asked about the jobs themselves, rely only on information given to you and provide clear facts."""
        },
        {
            "role": "user",
            "content": str(chat_history)
        }
    ]
    reply = llm.invoke(messages)
    chat_history.append(AIMessage(content = reply.content))
    print(reply.content)
    return {"messages": [{"role": "assistant", "content": reply.content}]}


def run_scrapers(state: State):
    print("REQUIRED JOBS TO BE SCRAPED.")
    struct_out_llm = llm.with_structured_output(JobsInfo)
    messages = [
        {"role": "system",
         "content": """Pick out the following fields from the input string.
                        site(optional): The job site to search for jobs on
                        search_term(optional): The post for which to search for jobs
                        google_search_term(optional): A string that contains post, location and time, used to search on Google Jobs
                        location(optional): The location to search for jobs in
                        results_wanted(optional): The number of results to return
                        hours_old(optional): The number of hours to search for jobs in the past
                        country_indeed(optional): The country to search for jobs in"""
        },
        {
            "role": "user",
            "content": str(chat_history)
        }
    ]
    result = struct_out_llm.invoke(messages)
    print(result)
    site_name, search_term, google_search_term, location, hours_old, results_wanted, country_indeed = refine_result(result)
    print(f"site_name = {site_name}, search_term = {search_term}, google_search_term = {google_search_term}, location = {location}, hours_old = {hours_old}, results_wanted = {results_wanted}, country_indeed = {country_indeed}")
    get_jobs(site_name, search_term, google_search_term, location, hours_old, results_wanted, country_indeed)
    chat_history.append(AIMessage(content = "Required jobs were scraped."))

def get_data_from_db(state: State):
    print("GET DATA FROM DATABASE")
    struct_out_llm = llm.with_structured_output(SearchFields)
    messages = [
        {"role": "system",
         "content": """Pick out the fields from the input string that are relevant to the user's query.
                        id(optional): The job IDs the user is asking about
                        site(optional): The job websites that the user is asking about
                        job_url(optional): The job URLs the user is asking about
                        job_url_direct(optional): The direct URLs the user is asking about
                        position(optional): The job positions the user is asking about
                        company(optional): The job companies that the user is asking about
                        location(optional): The locations that the user is asking about
                        date_posted(optional): The job posting dates the user is asking about
                        job_type(optional): The types of jobs the user is asking about"""
        },
        {
            "role": "user",
            "content": str(chat_history)
        }
    ]
    result = struct_out_llm.invoke(messages)
    print(result) # COMMENT THIS OUT LATER, ONLY FOR TESTING
    
    # 'result' is going to get the required search fields to search the database from the user's query in a structured format.
    # (Run the program and ask a question related to previous searches to make the agent come to this section.)
    # Here, use the class called 'result' and write code to get the data from database.
    # The declaration of the class (class name is SearchFields) is present in JobspyFuncs.py.
    # Then, replace "DATA FROM DATABASE" with the info you just got from the db.

    chat_history.append(AIMessage(content = "DATA FROM DATABASE"))
    messages = [
        {"role": "system",
         "content": """You are an agent who answers questions related to jobs that the user was previously interested in.
                        If the user wants details about previously searched jobs, give concise and clear facts.
                        If the user asks for your opinion, rely on real evidence and do not strongly suggest anything.
                        If asked about the jobs themselves, rely only on information given to you and provide clear facts."""
        },
        {
            "role": "user",
            "content": str(chat_history)
        }
    ]
    reply = llm.invoke(messages)
    chat_history.append(AIMessage(content = reply.content))
    print(reply.content)
    return {"messages": [{"role": "assistant", "content": reply.content}]}


graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("getjobs", getjobs_agent)
graph_builder.add_node("help", help_agent)
graph_builder.add_node("yesnoclassifier", yes_or_no)
graph_builder.add_node("jobrouter", job_router)
graph_builder.add_node("helpclassifier", classify_help)
graph_builder.add_node("helprouter", help_router)
graph_builder.add_node("dbhelp", get_data_from_db)
graph_builder.add_node("runscrapers", run_scrapers)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"getjobs": "getjobs", "help": "helpclassifier"}
)

graph_builder.add_edge("helpclassifier", "helprouter")

graph_builder.add_conditional_edges(
    "helprouter",
    lambda state: state.get("next"),
    {"general": "help", "database": "dbhelp"}
)

graph_builder.add_edge("getjobs", "yesnoclassifier")
graph_builder.add_edge("yesnoclassifier", "jobrouter")

graph_builder.add_conditional_edges(
    "jobrouter",
    lambda state: state.get("next"),
    {"scrape": "runscrapers", "end": "classifier"}
)

graph_builder.add_edge("runscrapers", END)
graph_builder.add_edge("help", END)
graph_builder.add_edge("dbhelp", END)

graph = graph_builder.compile()


def run_chatbot():
    state = {"messages": [], "message_type": None}
    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("\nBye! Have a nice day!")
            break
        chat_history.append(HumanMessage(content = user_input))
        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]
        state = graph.invoke(state)


if __name__ == "__main__":
    run_chatbot()