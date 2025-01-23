#
# Python script to refine a test case from a JIRA User Storyt using OpenAI's models.
# Creates the source BDD file for Agentic AI Framework
# Creates Zephyr Import files for JIRA Test Case issue Types
#
# Author: 	C. Finnegan
# Date:		January/February 2025
#


#!/usr/bin/env python3
import os
from dotenv import load_dotenv


# Set up your OpenAI API key
#os.environ["OPENAI_API_KEY"] = "mykey"
#os.environ["OPENAI_API_BASE"] = "https://genai-gateway.azure-api.net/"
#os.environ["JIRA_USER_NAME"] = "myjiraemail"
#os.environ["JIRA_API_TOKEN"] = "myjiratoken"

# Specify the path to the .env file
#env_path = os.path.join(os.path.dirname(__file__), '.env')
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'AINative_Env', '.env')
load_dotenv(dotenv_path=env_path)

# Access the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
JIRA_USER_NAME = os.getenv("JIRA_USER_NAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Your code can now use these variables
print(OPENAI_API_KEY)
print(OPENAI_API_BASE)
print(JIRA_USER_NAME)
print(JIRA_API_TOKEN)


from jiraextraction import retrieve_jira_ticket_from_server, create_jira_comments_in_chunks
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

# Initialize the language model
llm = ChatOpenAI(temperature=0.5, model="claude-3-5-sonnet-v2")
llmlowtemp = ChatOpenAI(temperature=0.1, model="claude-3-5-sonnet-v2")

# Create a prompt template
prompt = PromptTemplate.from_template("""
You are an expert on behaviour driven development (BDD) and agile refinement of stories for software development. Your task is to review and refine the following user story to ensure it is well-defined and ready for development.

Please consider the following aspects from the perspectives of a software developer, product owner, and QA engineer:
1. Clarity: Ensure the story is clear and concise.
2. Completeness: Make sure all necessary details are included.
3. Acceptance Criteria: Define clear acceptance criteria that match the story's requirements. 
4. Attempt to meet the agile INVEST guidelines but not critical if not possible. 
5. Example Mapping: Use example mapping to clarify requirements from the viewpoint of software developers, product owners, and QA engineers. 
Rules and acceptance criteria must align. Do not duplicate questions. All output of example mapping should have updated the Acceptance Criteria and Technical Requirements and Outstanding Questions.

Structure story in the following order Summary, Description and/or Business value, Acceptance criteria, Technical Requirements, Example Mapping Session, Outstanding Questions and finally any other Notes

The output should be formatted for a JIRA cloud comment and its supported markdown syntax. Use JIRA panels only to highlight problems or immediate things to confirm, but do use color to highlight other important sections and titles. Render in JIRA cloud markdown the color coding in the headings: Blue for Rules, Green for Examples, Red for Questions

Do not include a definition of done.

Here is the user story to refine:

Story to refine: 
Summary:{summary}
Description:{description}
""")

estimationPrompt = PromptTemplate.from_template("""
You are an expert in behaviour driven development (BDD) and agile refinement of user stories. Your task is to review the following user story and provide a T-shirt size estimate (S, M, L, ?) based on its clarity and completeness.
Please create a single sentence indicating the T-shirt size estimate. 
Ensure that the output is formatted for a JIRA cloud comment and adheres to its supported markdown syntax.
Here is the user story to estimate:
Summary:{summary}
Description:{refined_story}
""")

gherkinPrompt = PromptTemplate.from_template("""
You are an expert on behaviour driven development (BDD) and agile refinement of user stories. Your task is to create Gherkin code based on the refined user story and example mapping.
Ensure that the Gherkin code is clear, concise, and covers all necessary scenarios and wrapped in a jira code block.
Ensure the output is formatted for a JIRA cloud comment wrapped and adhere to its supported markdown syntax.
Here is the refined user story and example mapping:
Example mapping:{refined_story}
""")

# Function to ask a question
def bdd_refine(jira_ticket):
    ticket_data = retrieve_jira_ticket_from_server(jira_ticket)
    if ticket_data:
        story = {
            "summary": ticket_data.get('fields', {}).get('summary', 'No summary found'),
            "description": ticket_data.get('fields', {}).get('description', 'No description found')
        }
    
    # Create chains for each expertise
    refine_chain = prompt | llm | StrOutputParser()
    estimation_chain = estimationPrompt | llmlowtemp | StrOutputParser()
    gherkin_chain = gherkinPrompt | llmlowtemp |  StrOutputParser()
    
    # Invoke each chain sequentially
    final_response = refine_chain.invoke({"summary":story["summary"], "description": story["description"]})
    estimate_response = estimation_chain.invoke({"summary": story["summary"], "refined_story": final_response})
    gherkin_response = gherkin_chain.invoke({"refined_story": final_response})
    
    print("\nFinal Refined Story:")
    
    # Create a comment on the JIRA ticket with the refined story
    comment = f"h1. AI Refinement\n{estimate_response}\n\n{final_response}\n\n{gherkin_response}"
    print(comment)
    
    # Post the comment in chunks to JIRA
    create_jira_comments_in_chunks(jira_ticket, comment)
    
    return final_response

# Main application loop
if __name__ == "__main__":
    jira_ticket = "INVHUB-11696"  # Replace with the actual ticket number
    answer = bdd_refine(jira_ticket)