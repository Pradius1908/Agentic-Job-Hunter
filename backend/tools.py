import json
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


@tool
def company_parser_tool(company_name:str) -> str:
    print(f"Parsing company information for: {company_name} ")

    query=f"{company_name} company overview work culture employee reviews recent news"

    try:
        raw_search_results=web_search.run(query)
    except Exception as e:
        return f'{{"error": "Failed to fetch search results: {company_name}"}}'
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    prompt=PromptTemplate.from_template(
        """
        You are a helpful assistant that extracts relevant information about a company from search results. 
        Given the search results, extract the following information about the company:
        1. Company Overview: A brief description of the company, its industry, and its main products or services.
        2. Work Culture: Insights into the company's work environment, values, and employee satisfaction.
        3. Employee Reviews: A summary of employee reviews, highlighting common themes and sentiments.
        4. Recent News: A summary of recent news articles related to the company, including any major developments or controversies.

        Raw Search Results:
        {raw_data}
        
        Return ONLY the JSON. No markdown formatting blocks.

        Please provide the extracted information in a structured JSON format with the following keys: "company_overview", "work_culture", "employee_reviews", "recent_news".
        """
    )

    chain=prompt | llm

    try:
        result=chain.invoke({"raw_data": raw_search_results})
        return result.content
    except Exception as e:
        return f'{{"error": "Failed to extract company information: {company_name}"}}'