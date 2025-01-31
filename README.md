Refine JIRA tickets using BDD and example mapping.

Provide a gherkin template using this refinement.

Comment BDD Scenarios back to jira as a comment nicely formatted.

Build a Zephyr EXCEL import file for use in JIRA/Zephyr custom import




Prerequisites
* pip install os dotenv sys logging json pandas openpyxl requests textwrap



Config

* Configure your API and jira login within appropriate environment set up; API keys etc.

* Configure your JIRA ticket containing the functional requirements

* The \Prompts sub directory stores the text files containing the prompt templates used to generate the BDD scenarios and test cases.

* The 'GherkinPrompt.txt' and 'ZephyrTestCasePrompt.txt' contain the generic instructions to build the BDD and test case data respectively.

* The \Prompts sub directory also stores another text file with 'Additional' rules. This contains instructions on building
test cases that are specific to a particular application (Investigator Hub) in this case. The intention is to tailor the test cases better to the application. However, any changes to this file must try and avoid 'over-fitting' the instructions to a particular test case, which might impact on the LLMs ability to generalise test cases for the application.



To Execute

* Run the app.py application - command line expects python app.py <JIRA_TICKET> <EPIC_LINK> format.

* Review the generated BDD scenarios in the JIRA ticket comments. Review test cases in the output file: 'Zephyr_Test_Cases_Output.xlsx'.

* Load XL file created by app through custom Zephyr Import interface - external action.
