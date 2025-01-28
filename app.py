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
import sys
import logging
import json




# Specify the path to the .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'AINative_Env', '.env')
load_dotenv(dotenv_path=env_path)

# Access the environment variables
# Set up your OpenAI API and JIRA keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
JIRA_USER_NAME = os.getenv("JIRA_USER_NAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Your code can now use these variables
# print(OPENAI_API_KEY)
# print(OPENAI_API_BASE)
# print(JIRA_USER_NAME)
# print(JIRA_API_TOKEN)

# Import custom functions to extract JIRA requirements data
from jiraextraction import retrieve_jira_ticket_from_server, create_jira_comments_in_chunks, add_label_to_jira_ticket

# Import custom function to generate Excel file used as inout for Zephyr Squad Internal Import utilty
from ZephyrImport import generate_excel_from_json

# Import LangChain modules
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

# Initialize the language model
llm = ChatOpenAI(temperature=0.5, model="claude-3-5-sonnet-v2")
llmlowtemp = ChatOpenAI(temperature=0.1, model="claude-3-5-sonnet-v2")

# Set up file name structure for JSON files output/input of Test Cases
sFile_TC_suffix = "_test_case_steps"

# Create a prompt template
prompt = PromptTemplate.from_template("""
You are an expert on behaviour driven development (BDD) and agile refinement of stories for software development. Your task is to review and refine the following user story to ensure it is well-defined and ready for development.

Key Guidelines:
1. You can revise existing content in the story, but DO NOT invent or assume requirements that aren't explicitly stated
2. If details are missing, add them to Outstanding Questions rather than making assumptions
3. Only provide acceptance criteria and examples for clearly stated requirements
4. Flag ambiguity and missing information rather than filling in gaps

INVEST Analysis (analyze only what's provided, flag missing aspects):
- Independent: Can this story be delivered independently? Flag dependencies.
- Negotiable: Is there room for discussion, or is it too prescriptive?
- Valuable: Is the business value clearly stated?
- Estimable: Is there enough detail to estimate? Please create a single sentence indicating the T-shirt size estimate if possible, otherwise flag what's missing.
- Small: Can it be completed in one sprint?
- Testable: Are the requirements clear enough to test?

Please consider the following aspects from the perspectives of a software developer, product owner, and QA engineer:
1. Clarity: Ensure the story is clear and concise.
2. Completeness: Make sure all necessary details are included.
3. Acceptance Criteria: Define clear acceptance criteria that match the story's requirements
4. Example Mapping: Only if sufficient acceptance criteria exist in the story, use example mapping to clarify requirements further from the viewpoint of software developers, product owners, and QA engineers. 
Rules and acceptance criteria must align.

Structure your response in this order:
- Immediate Concerns/INVEST Analysis
- Summary
- Description/Business Value
- Proposed Acceptance Criteria
- Examples
- Technical Requirements (only if clearly implied by the story)
- Outstanding Questions (highlight all missing critical information)
- Notes (optional observations)

The output should be formatted for a JIRA cloud comment and its supported markdown syntax. Use JIRA panels only to highlight problems or immediate things to confirm, but do use color to highlight other important sections and titles. Render in JIRA cloud markdown the color coding in the headings: Blue for Rules/Acceptance Criteria, Green for Examples, Red for Questions

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
Rules:
1. Each scenario must map to a specific acceptance criterion
2. Use concrete examples, not abstract ones
3. Focus on business outcomes, not technical implementation
4. Only return the gherkin code, DO NOT provide any additional information
Ensure the output is formatted for a JIRA cloud comment wrapped and adhere to its supported markdown syntax.
Here is the refined user story and example mapping:
Example mapping:{refined_story}
""")

jsonTestCasePrompt = PromptTemplate.from_template("""
You are a Zephyr test case expert using the Zephyr Squad plug-in in the company Atlassian Cloud JIRA instance. 
Generate detailed QA test cases for each Scenario identified in the Gherkin file, and return all the test cases as a structured JSON object. 
Rules:
1. Include the steps, expected results, and any preconditions or postconditions.
2. Each test step must have a corresponding expected result.
3. Generate a brief text assumption about possible test data required and add that comment to the response.
Here is the Gherkin formatted test case scenarios to reformat into the json test case format for which an example json format is provided:
Test Scenarios:{bdd_test_scenarios}
Example json: {json_sample}
""")

def load_sample_json():
    with open("Sample_Zephyr_test_case_steps.json", "r") as f:
        return json.load(f)
    
def trim_json_file(input_file_path):
    try:
        # Read the entire content of the file
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Find the position of the last '}' character
        last_brace_index = content.rfind('}')

        # Check if '}' was found
        if last_brace_index == -1:
            raise ValueError("No closing brace '}' found in the file.")

        # Keep only the content up to and including the last '}'
        trimmed_content = content[:last_brace_index + 1]

        # Write the trimmed content back to the file (or to a new file if needed)
        with open(input_file_path, 'w', encoding='utf-8') as file:
            file.write(trimmed_content)

        #print(f"\nFile {input_file_path} has been trimmed successfully.")

    except Exception as e:
        print(f"\nAn error occurred in the output LLM text file trim process: {e}")    
    

def format_json(input_file_path):
    #print("\nformat_json function...")
    # Define the path to your input and output files
    #input_file_path = 'output_LLM_test_case Response.txt'
    output_file_path = f"{jira_ticket}{sFile_TC_suffix}.json"

    # Trim the text file to remove any extra content
    trim_json_file(input_file_path)
    
    # Read the JSON content from the text file
    with open(input_file_path, 'r', encoding='utf-8') as file:
        # Load the content of the file into a dictionary
        data = json.load(file)

    # Write the loaded data to a new JSON file
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        # dump the dictionary to the JSON file with indentation for readability
        json.dump(data, json_file, indent=4)

    print(f"\nStage 3c: Data has been successfully converted to {output_file_path}")


# Function to ask a question
def bdd_refine(jira_ticket, epic_link):

    global sFile_TC_suffix

    ticket_data = retrieve_jira_ticket_from_server(jira_ticket)
    if ticket_data:
        story = {
            "summary": ticket_data.get('fields', {}).get('summary', 'No summary found'),
            "description": ticket_data.get('fields', {}).get('description', 'No description found')
        }
    
    # Create chains for each expertise
    print("\nStage 1a: Creating chains for each expertise...")
    refine_chain = prompt | llm | StrOutputParser()
    estimation_chain = estimationPrompt | llmlowtemp | StrOutputParser()
    gherkin_chain = gherkinPrompt | llmlowtemp |  StrOutputParser()
    jsontestcase_chain = jsonTestCasePrompt | llmlowtemp |  StrOutputParser()
   
    
    # Invoke each chain sequentially
    print("\nStage 1b: Invoking and processing each chain sequentially...")
    final_response = refine_chain.invoke({"summary":story["summary"], "description": story["description"]})
    estimate_response = estimation_chain.invoke({"summary": story["summary"], "refined_story": final_response})
    gherkin_response = gherkin_chain.invoke({"refined_story": final_response})
    testcase_response = jsontestcase_chain.invoke({"bdd_test_scenarios": gherkin_response, "json_sample": load_sample_json()})
    
    print("\nStage 1c: Final Refined Story generated:...")
    
    # Create a comment on the JIRA ticket with the refined story
    #comment = f"h1. AI Refinement\n{estimate_response}\n\n{final_response}\n\n{gherkin_response}"
    comment = f"h1. AI Refinement Gherkin:\n{gherkin_response}"
    #print("\ncomment...")
    #print(comment)
    
    print("\nStage 2a: Updating JIRA ticket with BDD content...")
    # Post the comment in chunks to JIRA
    add_label_to_jira_ticket(jira_ticket, "#ai")
    create_jira_comments_in_chunks(jira_ticket, comment)


    print("\nStage 3a: Build Zephyr Import file:...")
    #print("\nTest Case Response returned from LLM...")
    #print(type(testcase_response))
    #print(testcase_response)

    # Writing Test Case Response from LLM to a text file
    #print("\nWriting Test Case Response from LLM to a text file...")
    txt_file_name = f"{jira_ticket}{sFile_TC_suffix}.txt"
    with open(txt_file_name, 'w') as jfile:
        # Write the string to the file
        jfile.write(testcase_response)

    # Format the text response from the LLM to a JSON file
    print("\nStage 3b: Converting Test Case Response from LLM to a JSON file...")
    format_json(txt_file_name)
    # tc_Response = parseLLM_TCResponse(testcase_response)

    # print("\nConvert LLM Str Response string to JSON...")
    # output_json = json.dumps(testcase_response, indent=4)
    # print("\noutput_json type...")
    # print(type(output_json))

    # Set up file name structure for JSON files output/input of Test Cases
    #sFile_TC_suffix = "_test_case_steps"    

    # if tc_Response is not None:
    if testcase_response is not None:
                                               
        # Write the successful JSON output to a file
       
        try:
            json_file_name = f"{jira_ticket}{sFile_TC_suffix}.json"
            generate_excel_from_json(json_file_name, epic_link)
            logging.info("\n Successfully Generated AI Content and Created XL for Zephyr Squad Import\n")
        except Exception as e:
            logging.error(f"Error generating Excel file: {e}")
            print(f"Error generating Excel file: {e}")
    
    return final_response

# Main application loop
if __name__ == "__main__":

     # Input the JIRA ticket number as a command line parameter
     # Use LangChain to build a refined BDD test case from the JIRA User Story
     # Build an XL from these test cases to use in Zephyr Squad Internal Import utility


    if len(sys.argv) != 3:
        print("Usage: python app.py <JIRA_TICKET> <EPIC_LINK>")
    else:
 
        # python app.py INVHUB-11696 INVHUB-10821 - Sample Cmd Line Call

        # Get the JIRA Ticket from command line arguments
        jira_ticket = sys.argv[1]
        # Get the epic link from command line arguments
        epic_link = sys.argv[2]

        answer = bdd_refine(jira_ticket, epic_link)