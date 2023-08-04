
import ast

# Constants for the output string format
FILE_MSG = "{} contains the following elements:\n"
FUNC_MSG = "def {}({})\n"

def extract_functions(python_file_content, python_file_name):
    # Parse the python file content into an abstract syntax tree
    ast_tree = ast.parse(python_file_content)

    # Initialize the output string with the filename
    output_string = FILE_MSG.format(python_file_name)

    # Iterate over all top-level functions in the abstract syntax tree
    for node in ast.iter_child_nodes(ast_tree):
        if isinstance(node, ast.FunctionDef):
            # Extract the function name
            func_name = node.name

            # Extract the function parameters
            func_params = [arg.arg for arg in node.args.args]

            # Add the function interface to the output string
            output_string += FUNC_MSG.format(func_name, ', '.join(func_params))

    return output_string
