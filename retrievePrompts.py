"""
The purpose of this file is to retrieve the prompts for the Langchain model.

The prompts are used to guide the user in providing the necessary information for the Langchain model to process.


"""
import logging

# Function to retrieve the prompts
from langchain_core.prompts import PromptTemplate


def retrieve_TestCasePrompt():

    # Define the path to the file
    file_path = 'Prompts/Zephyr/ZephyrTestCasePrompt.txt'

    # Open the file and read its contents into a string variable
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # Now the content of the file is stored in the variable 'file_content'
    print("\n\n\nThis is the content of the prompt to generate Test Cases (Json) to parse into Zephyr Squad Imports\n")
    print(file_content)
    # Function to retrieve the prompts

    return file_content



def retrieve_GherkinPrompt():

    # Define the path to the file
    sGfile_path = 'Prompts/Gherkin/GherkinPrompt.txt'

    # Open the file and read its contents into a string variable
    with open(sGfile_path, 'r', encoding='utf-8') as file:
        fGfile_content = file.read()

    # Now the content of the file is stored in the variable 'file_content'
    print("\n\n\nThis is the content of the prompt to generate Gherkin Feature Files to be used for Test Agent Automation\n")
    print(fGfile_content)
    # Function to retrieve the prompts

    return fGfile_content



def retrieve_EstimatePrompt():

    # Define the path to the file
    sEfile_path = 'Prompts/Estimate/EstimatePrompt.txt'

    # Open the file and read its contents into a string variable
    with open(sEfile_path, 'r', encoding='utf-8') as file:
        fEfile_content = file.read()

    # Now the content of the file is stored in the variable 'file_content'
    print("\n\n\nThis is the content of the prompt to generate a T-Shirt work estimate for the JIRA requirement\n")
    print(fEfile_content)
    # Function to retrieve the prompts

    return fEfile_content


def retrieve_MainPrompt():

    # Define the path to the file
    sMfile_path = 'Prompts/Main/Prompt.txt'

    # Open the file and read its contents into a string variable
    with open(sMfile_path, 'r', encoding='utf-8') as file:
        fMfile_content = file.read()

    # Now the content of the file is stored in the variable 'file_content'
    print("\nThis is the content of the initial prompt\n")
    print(fMfile_content)
    # Function to retrieve the prompts

    return fMfile_content



def retrieve_Prompts():

    print("\nStage 0: Retrieving text for prompts from file directories...")
    logging.info("Retrieving text for prompts from file directories.")   

   
    # Retrieve the main initial prompt template for the LLM to generate the BDD/Test Case output
    sPrompt = retrieve_MainPrompt()
    prompt = PromptTemplate.from_template(sPrompt)

    # Retrieve the prompt template for the LLM to generate the work T-Shirt size estimate
    sEst_Prompt = retrieve_EstimatePrompt()
    estimationPrompt = PromptTemplate.from_template(sEst_Prompt)

    # Retrieve the prompt template for the LLM to generate the Gherkin text
    sGk_Prompt = retrieve_GherkinPrompt()
    gherkinPrompt = PromptTemplate.from_template(sGk_Prompt)

    # Retrieve the prompt template for the LLM to generate the test case (Json format)
    sTC_Prompt = retrieve_TestCasePrompt()
    jsonTestCasePrompt = PromptTemplate.from_template(sTC_Prompt)

    

    return prompt, estimationPrompt, gherkinPrompt, jsonTestCasePrompt