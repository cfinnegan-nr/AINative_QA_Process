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



# --------
# Custom Imports
# --------
# Import custom functions to extract JIRA requirements data
from jiraextraction import retrieve_jira_ticket_from_server, create_jira_comments_in_chunks, add_label_to_jira_ticket

# Import custom function to extract Atlassian Confluence requirements data
from confluenceextraction import get_page_content

# Import custom function to generate Excel file used as inout for Zephyr Squad Internal Import utilty
from ZephyrImport import build_Zephyr_Import_File, generate_excel_from_json

# Import custom functions to format the JSON output from the LLM
from dataformatting import load_sample_json

# Import custom function to retrieve the prompts
from retrievePrompts import retrieve_Prompts, get_additional_Gherkin_rules, get_additional_Zephyr_rules


# Import LangChain modules
#from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter



# Import the LangChain module
# Initialize the language model

llm = ChatOpenAI(temperature=0.5, model="claude-3-5-sonnet-v2")
llmlowtemp = ChatOpenAI(temperature=0.1, model="claude-3-5-sonnet-v2")
llmlowertemp = ChatOpenAI(temperature=0.05, model="claude-3-5-sonnet-v2")



# Primary Function to retrieve the JIRA ticket data and build BDD output 
# and Import files (EXCEL) for the Zephyr Squad Internal Import utility
def generate_BDDs_Zephyr_Imports(jira_ticket, epic_link, iteration_number, page_id="n/a"):

    # Set up file name structure for JSON files output/input of Test Cases
    sFile_TC_suffix = "_test_case_steps"

    # Retrieve the JIRA ticket data
    ticket_data = retrieve_jira_ticket_from_server(jira_ticket, "STORY")

    # Get confluence content
    confluence_content = get_page_content(page_id) if page_id.isdigit() else None

    # Get epic details using retrieve_jira_ticket_from_server
    context_ticket_data = retrieve_jira_ticket_from_server(epic_link, "EPIC") if epic_link else None

    # Combine design context
    design_context = ""
    if confluence_content:
        design_context += "\nh2. Additional Context: Confluence Design Documentation\n" + confluence_content + "\n\n"
    if context_ticket_data:
        design_context += "\n\nh2. Additional Context from EPIC or related ticket: \n"
        design_context += f"Epic Summary: {context_ticket_data.get('fields', {}).get('summary', 'No epic summary found')}\n"
        design_context += f"Epic Description: {context_ticket_data.get('fields', {}).get('description', 'No epic description found')}\n"

    # Display Design Context Information
    print(f"\nConfluence + JIRA EPIC content looks like...{design_context}")
 

    if ticket_data:
        story = {
            "summary": ticket_data.get('fields', {}).get('summary', 'No summary found'),
            "description": ticket_data.get('fields', {}).get('description', 'No description found'),
            "issue": ticket_data.get('issuetype', 'No issuetype found'),
            "context": design_context if design_context else "No additional context available"
        }

    # Retrieve the prompts
    prompt, estimationPrompt, gherkinPrompt, jsonTestCasePrompt = retrieve_Prompts()
    
    # Create chains for each expertise
    try:
        # Inform the user that the process of creating chains has started
        print("\nStage 1a: Creating chains for each expertise...")
    
        # Create a refinement chain using the prompt, language model, and output parser
        refine_chain = prompt | llm | StrOutputParser()
    
        # Create an estimation chain using the estimation prompt, low temperature language model, and output parser
        estimation_chain = estimationPrompt | llmlowtemp | StrOutputParser()
    
        # Create a Gherkin chain using the Gherkin prompt, low temperature language model, and output parser
        gherkin_chain = gherkinPrompt | llmlowertemp | StrOutputParser()
    
        # Create a JSON test case chain using the JSON test case prompt, low temperature language model, and output parser
        jsontestcase_chain = jsonTestCasePrompt | llmlowertemp | StrOutputParser()
    
    except Exception as e:
        # Catch any exception that occurs during the chain creation process
        # Log the exception message for debugging purposes
        print(f"An error occurred while creating chains: {e}")
   
    print("\nThese are the additional rules added to the Gherkin prompt:")
    print("\n", get_additional_Gherkin_rules())

    print("\nThese are the additional rules added to the Test Case/Zephyr Import prompt:")
    print("\n", get_additional_Zephyr_rules())


    # Invoke each chain sequentially
    print("\nStage 1b: Invoking and processing each chain sequentially...")
    
    try:
        iterations = int(iteration_number.strip())
        print(f"\nNumber of iterations for main and test case json prompt: {iterations}")
        final_response = story["description"] 
          
        # Invoke main chain to refine the story through multiple iterations
        num = 0
        while num < iterations:
            num = num + 1
            final_response = refine_chain.invoke({"summary":        story["summary"], 
                                                  "description":    final_response, 
                                                  "issue":          story["issue"], 
                                                  "context":        story["context"]})
            print(f"\n Refinement Iteration: {num}...")

        # Invoke the estimation_chain with the summary and the refined story
        estimate_response = estimation_chain.invoke({"summary":         story["summary"], 
                                                     "refined_story":   final_response})
        
        # Invoke the gherkin_chain with the refined story
        gherkin_response = gherkin_chain.invoke({"refined_story":       final_response, 
                                                 "additional_rules":    get_additional_Gherkin_rules()})
        
        
        # testcase_response = jsontestcase_chain.invoke({"bdd_test_scenarios": gherkin_response, 
        #                                                "json_sample": load_sample_json(), 
        #                                                "additional_rules": get_additional_Zephyr_rules()})

        # Invoke the jsontestcase_chain with the BDD test scenarios and a sample JSON
        # Invoke main chain to refine the story through multiple iterations
        testcase_response = load_sample_json()
        numTCIt = 0             
        while numTCIt < iterations:
            numTCIt = numTCIt + 1
            testcase_response = jsontestcase_chain.invoke({"bdd_test_scenarios": gherkin_response, 
                                                           "json_sample":        testcase_response, 
                                                           "additional_rules":   get_additional_Zephyr_rules()})                                                       

    
    except Exception as e:
        # Print the exception message if any of the invocations fail
        print(f"An error occurred during the chain invocation process: {e}")
    

    print("\nStage 1c: Final Refined Story generated:...")
    
    # Create a comment on the JIRA ticket with the refined BDD data (Gherkin format)
    comment = f"h1. AI Refinement After {num} Iteration(s) for BDD Scenarios:\n{gherkin_response}"
    print(f"\nGherkin (BDD Scenarios) response looks like...{comment}")

    print("\nStage 2a: Updating JIRA ticket with BDD content...")
    # Post the comment in chunks to JIRA
    add_label_to_jira_ticket(jira_ticket, "#ai")
    create_jira_comments_in_chunks(jira_ticket, comment)


    # if the LLM has responded with suggested test cases 
    # then write the test cases to a file for Zephyr Squad impor:
    if testcase_response is not None:
        
        # Writing Test Case Response from LLM to a text file
        txt_file_name = f"{jira_ticket}{sFile_TC_suffix}.txt"
        # Prepare the JSON file name for output
        json_file_name = f"{jira_ticket}{sFile_TC_suffix}.json"

        # Write the LLM test case response output to a file to load into Zephyr Squad
        build_Zephyr_Import_File(testcase_response,
                                 txt_file_name, 
                                 json_file_name, 
                                 epic_link)
    else:
        print("\nNo test cases generated by the LLM...")
        logging.error("LLM response was empty. No test cases generated.")    




# Main application loop
if __name__ == "__main__":

     # Input the JIRA ticket number as a command line parameter
     # Use LangChain to build a refined BDD test case from the JIRA User Story
     # Build an XL from these test cases to use in Zephyr Squad Internal Import utility


    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python app.py <JIRA_TICKET> <EPIC_LINK> <Iteration Number> [Confluence Page ID]")
    else:
 
        # python app.py INVHUB-11696 INVHUB-10821 1 1- Sample Cmd Line Call

        # Get the JIRA Ticket from command line arguments
        jira_ticket = sys.argv[1]
        # Get the epic link from command line arguments
        epic_link = sys.argv[2]
        # Get the iteration number from command line arguments
        iteration_number = sys.argv[3]

        # Get the optional Confluence page ID, default to None if not provided
        # confluence_page_id = sys.argv[4] if len(sys.argv) == 5 else "n/a"
        confluence_page_id = sys.argv[4] if len(sys.argv) == 5 else "402817082"


        generate_BDDs_Zephyr_Imports(jira_ticket, epic_link, iteration_number, confluence_page_id)
        print("\nProcess completed successfully!\n")