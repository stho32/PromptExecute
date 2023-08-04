
import ast

# Constants for repeated strings
FILE_CONTAINS_MSG = " contains the following elements:\n"
DEF_MSG = "def "

def extract_functions(file_content, file_name):
    """
    This function takes the content of a python file and its filename as input.
    It parses the file, extracts the function names and their parameters, and 
    returns a string that lists the functions and their parameters.
    """
    # Parse the content of the file into an AST
    module = ast.parse(file_content)

    # Initialize the output string with the filename
    output_string = './' + file_name + FILE_CONTAINS_MSG

    # Traverse the AST
    for node in ast.walk(module):
        # If the node is a function
        if isinstance(node, ast.FunctionDef):
            # Get the function name
            function_name = node.name

            # Get the function parameters
            function_params = [arg.arg for arg in node.args.args]

            # Add the function interface to the output string
            output_string += DEF_MSG + function_name + '(' + ', '.join(function_params) + ')\n'

    return output_string
