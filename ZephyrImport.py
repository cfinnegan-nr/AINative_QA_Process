import pandas as pd
import json
from   openpyxl import Workbook
import logging

# Import custom functions to format the JSON output from the LLM
from dataformatting import format_json


"""
    The AI response has been parsed and the test cases are now available in a JSON format.
    The next step is to convert the JSON data into an Excel file that can be imported into Zephyr. 
    The Excel file should have the following columns: 
        "External id", "Test Summary", "OrderId", "Step", "Test Data", 
        "Expected Result", "Assigned To", "Comments", "Description", "Component", 
        "jira-customfield-checkbox", "Epic Link", "Linked issues", "Labels", "Issue Key [To add steps]".
    The Excel file should be saved as "Zephyr_Test_Cases_Output.xlsx".

    For simplicty, some dummy variabels have been hardcoded in the function. 


"""

def build_Zephyr_Import_File(testcase_response,
                             txt_file_name, 
                             json_file_name, 
                             epic_link):
        
        print("\nStage 3a: Build Zephyr Import file:...")

        try:
            with open(txt_file_name, 'w') as jfile:
                # Write the string to the file
                jfile.write(testcase_response)
        except IOError as e:
            # Handle file I/O errors
            print(f"An error occurred while writing to the file: {e}")

        # Format the text response from the LLM to a JSON file
        print("\nStage 3b: Converting Test Case Response from LLM to a JSON file...")
        format_json(txt_file_name, json_file_name)
  
                                               
        # Write the successful JSON output to a file    
        try:
            #json_file_name = f"{jira_ticket}{sFile_TC_suffix}.json"
            generate_excel_from_json(json_file_name, epic_link)
            logging.info("\n Successfully Generated AI Content and Created XL for Zephyr Squad Import\n")
        except Exception as e:
            logging.error(f"Error generating Excel file: {e}")
            print(f"Error generating Excel file: {e}")



def generate_excel_from_json(json_file, epic_link):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)

        # print("\ngenerate_excel_from_json function...")
        # print(type(data))
        # print(data)

        test_cases = data.get('testCases', [])
        logging.info(f"Stage 4a - JSON file '{json_file}' loaded successfully.")
        wb = Workbook()

        id_counter = 1

        for sheet_index, test_case in enumerate(test_cases, start=1):
            # Create a new sheet for each test case
            if sheet_index == 1:
                ws = wb.active
                ws.title = f"Sheet{sheet_index}"
            else:
                ws = wb.create_sheet(title=f"Sheet{sheet_index}")

            # Set up headers
            headers = [
                "External id", "Test Summary", "OrderId", "Step", "Test Data",
                "Expected Result", "Assigned To", "Comments", "Description", 
                "Component", "jira-customfield-checkbox", "Epic Link", 
                "Linked issues", "Labels", "Issue Key [To add steps]", 
                "Issue Link Type", "Issues Key To Link", "Priority", "Sprint", 
                "Version", "Cascade"
            ]
            ws.append(headers)

            preconditions = test_case.get('preconditions', '')
            postconditions = test_case.get('postconditions', '')
            description = f"{preconditions}\n{postconditions}"

            for order_id, step in enumerate(test_case.get('steps', []), start=1):
                row = [
                    id_counter,  # External id
                    test_case.get('summary', ''),  # Test Summary
                    order_id,  # OrderId
                    step.get('step', ''),  # Step
                    step.get('testData', ''), # Test Data 
                    step.get('expectedResult', ''),  # Expected Result
                    "6414a0cd67102fc717c034d7",  # Assigned To C. Finnegan
                    "This test case has been built by GenAI Workbench for XL import via Internal Importer.",  # Comments
                    description,  # Description
                    "Core",  # Component
                    "external",  # jira-customfield-checkbox
                    epic_link,  # Epic Link
                    "blocks",  # Linked issues - Dummy value
                    "AINative(GenAI_Test_Case)",  # Labels
                    "IM-5000",  # Issue Key [To add steps] - Dummy value
                    "blocks",  # Issue Link Type - Dummy value
                    "IM-3000",  # Issues Key To Link - Dummy value
                    "3 - Medium",  # Priority
                    37,  # Sprint - Dummy value for Sprint ID ('Nice to Have Sprint' Ref)
                    "Release-1.0",  # Version - Dummy value
                    "Dublin"  # Cascade - Dummy value
                ]
                ws.append(row)

            id_counter += 1

        # Save the workbook
        output_file = "Zephyr_Test_Cases_Output.xlsx"
        wb.save(output_file)
        print((f"\nStage 4: Excel file '{output_file}' created successfully.\n"))
        logging.info(f"Stage 4b - Excel file '{output_file}' created successfully.")

    except FileNotFoundError:
        print(f"The file '{json_file}' does not exist.")
    except json.JSONDecodeError:
        print("Error decoding JSON. Please check the format of the input file.")
    except Exception as e:
        print(f"An error occurred: {e}")