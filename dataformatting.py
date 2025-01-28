import json

"""
    The AI response for the test case structure needs to be converted to a JSON file.

    This JSON file will be used to generate the Excel file that can be imported into Zephyr.

"""


def load_sample_json():
    """
    Load the sample JSON file that contains the structure of the test case steps.
    This is used as a template to format the AI response into a JSON file style response.
    """    
    try:
        with open("Sample_Zephyr_test_case_steps.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("The file was not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON from the file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return data    
    

    
def trim_txt_file(input_file_path):
    """
    The LLM will add text either before and after the JSON content that needs to be removed.

    This function will trim the text file to only include the JSON content.

    The additional text will be written to two separate files for review. It contains assumptions made by the LLM
    that could provide valuable information for the test case revision process.
    """ 
    try:
        # Read the entire content of the file
        with open(input_file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Find the position of the first "{" character
        brace_start_index = content.find('{')

        # Check if "{" was found
        if brace_start_index == -1:
            raise ValueError("No '{' character found in the file.")

        # Write the content before the "{" character to 'Test Cases Assumptions One'
        with open('Test Cases Assumptions One.txt', 'w', encoding='utf-8') as file:
            file.write(content[:brace_start_index])

        # Keep only the content after the "{" character
        trimmed_content_after_brace = content[brace_start_index:]

        # Find the position of the last '}' character
        last_brace_index = trimmed_content_after_brace.rfind('}')

        # Check if '}' was found
        if last_brace_index == -1:
            raise ValueError("No closing brace '}' found in the file after the '{' character.")

        # Keep only the content up to and including the last '}'
        trimmed_content = trimmed_content_after_brace[:last_brace_index + 1]

        # Write the trimmed content back to the original file
        with open(input_file_path, 'w', encoding='utf-8') as file:
            file.write(trimmed_content)

        # Write the content beyond the last '}' character to 'Test Cases Assumptions Two'
        if last_brace_index + 1 < len(trimmed_content_after_brace):
            with open('Test Cases Assumptions Two.txt', 'w', encoding='utf-8') as file:
                file.write(trimmed_content_after_brace[last_brace_index + 1:])

    except Exception as e:
        print(f"\nAn error occurred in the output LLM text file trim process: {e}")
    

def format_json(input_file_path, output_file_path):

    # Define the path to output files
    #output_file_path = f"{jira_ticket}{sFile_TC_suffix}.json"

    # Trim the text file to remove any extra content
    trim_txt_file(input_file_path)
    
    # Read the JSON content from the text file
    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            # Load the content of the file into a dictionary
            data = json.load(file)
    
        # Write the loaded data to a new JSON file
        with open(output_file_path, 'w', encoding='utf-8') as json_file:
            # dump the dictionary to the JSON file with indentation for readability
            json.dump(data, json_file, indent=4)
    
        print(f"\nStage 3c: Data has been successfully converted to {output_file_path}")
    
    except FileNotFoundError as e:
        print(f"Error: The file {e.filename} was not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from the file {input_file_path}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")