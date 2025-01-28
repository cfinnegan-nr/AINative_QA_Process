Refine JIRA tickets using BDD and example mapping.

Provide a gherkin template using this refinement.

Comment BDD Scenarios back to jira as a comment nicely formatted.

Build a Zephyr EXCEL import file for use in JIRA/Zephyr custom import

Prerequisites
* pip install os dotenv sys logging json pandas openpyxl requests textwrap

Config
* Configure your API and jira login within appropriate environment set
* Configure your jira_ticket
* Run the app.py application - command line expects python app.py <JIRA_TICKET> <EPIC_LINK> format.
* Load XL file created by app through custom Zephyr Import interface - external action.
