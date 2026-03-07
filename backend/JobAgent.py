from langchain_google_genai import ChatGoogleGenerativeAI
from JobspyFuncs import make_agent, make_dumb_agent, refine_result, get_jobs, chat_history, dumb_llm
from ApifyFuncs import client, indeedToJSON, naukriToJSON
from langchain_core.messages import HumanMessage, AIMessage
from math import ceil

# this bro takes the input and extracts job fields from it
agent = make_agent()

# this bro (paapa he's not really dumb) just summarises the job description in a few sentences cause Apify returns a HUGE html like output
dumb_agent = make_dumb_agent()

prompt = ""

# my comments are how you know I didn't chatgpt this

answer = dumb_agent.invoke({
    "messages": [{"role": "user", "content": "Naukri is an Indian job search company."}]
})
for key in answer:
    print(key)

while (prompt != "exit"):
    prompt = input("Enter gemini prompt: ")
    if (prompt == "exit"):
        break
    chat_history.append(HumanMessage(content = prompt))
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": str(chat_history)}]
        })
        site_name, search_term, google_search_term, location, hours_old, results_wanted, country_indeed = refine_result(result)
        chat_history.append(AIMessage(content = str(result["structured_response"])))
        get_jobs(site_name, search_term, google_search_term, location, hours_old, results_wanted, country_indeed)
    except TypeError:
        isApify = input("JobSpy Job Scraper failed. Use Apify to scrape jobs? (yes/no): ")
        if (isApify != "yes"):
            continue
        
        # I split results wanted between the different websites.
        results_to_fetch = results_wanted/ceil(len(site_name))

        if ("indeed" in site_name and results_wanted > 0):
            run_input = indeedToJSON(site_name, search_term, location, results_to_fetch, country_indeed)
            run = client.actor("hMvNSpz3JnHgl5jkh").call(run_input=run_input)
            results_wanted - results_wanted - results_to_fetch
        
        if ("naukri" in site_name and results_wanted > 0):
            run_input = naukriToJSON(search_term, location, results_to_fetch, country_indeed)
            run = client.actor("fnlYCvgCjrYJWbyRJ").call(run_input=run_input)
            results_wanted - results_wanted - results_to_fetch
        
        # not really sure how to put this data into a csv.

        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            answer = dumb_agent.invoke({
                "messages": [{"role": "user", "content": str(item)}]
            })
            # Not sure how to print the output. Also append the output to chat history as AIMessage.