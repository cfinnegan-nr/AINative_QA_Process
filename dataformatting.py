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
    

def format_json(input_file_path, output_file_path):

    # Define the path to output files
    #output_file_path = f"{jira_ticket}{sFile_TC_suffix}.json"

    # Trim the text file to remove any extra content
    trim_json_file(input_file_path)
    
    import json
    
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