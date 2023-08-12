import os
import sys
from library import configuration, change_detection, chatgpt

# Constants
INCLUDE_TAG = "#include"
WRITE_TO_TAG = "#write-to"
CODE_BLOCK_START = "```"
CODE_BLOCK_START_PYTHON = "```python"
CODE_BLOCK_END = "```"

def process_file(file_path):
    """
    Process a given file, prepare the prompt, call GPT-4, and perform post-processing.
    """
    print(f"Processing file: {file_path}")
    prepared_prompt, output_file_name = prepare_prompt(file_path)
    completed_file_path = file_path + ".completed"
    with open(completed_file_path, 'w') as completed_file:
        completed_file.write(prepared_prompt)
    print(f"Saved prepared prompt to: {completed_file_path}")

    gpt4_key = configuration.get_gpt4_key()
    gpt4_output = chatgpt.call_gpt_4(gpt4_key, prepared_prompt)
    output_file_path = file_path + ".output"
    with open(output_file_path, 'w') as output_file:
        output_file.write(gpt4_output)
    print(f"Saved GPT-4 output to: {output_file_path}")

    if output_file_name:
        post_process(gpt4_output, output_file_name)

def prepare_prompt(file_path):
    """
    Prepare the prompt by reading the file and handling include and write-to directives.
    """
    print(f"Preparing prompt for file: {file_path}")
    prepared_prompt = ""
    output_file_name = None
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith(INCLUDE_TAG):
                include_file_path = os.path.join(os.path.dirname(file_path), line[len(INCLUDE_TAG):].strip())
                with open(include_file_path, 'r') as include_file:
                    prepared_prompt += include_file.read() + "\n"
            elif line.startswith(WRITE_TO_TAG):
                output_file_name = os.path.join(os.path.dirname(file_path), line[len(WRITE_TO_TAG):].strip())
            else:
                prepared_prompt += line
    return prepared_prompt, output_file_name

def post_process(gpt4_output, output_file_name):
    """
    Post-process the GPT-4 output by extracting code blocks and writing them to the specified output file.
    """
    print(f"Post-processing GPT-4 output for file: {output_file_name}")
    code_blocks = extract_code_blocks(gpt4_output)
    with open(output_file_name, 'w') as output_file:
        output_file.write("\n".join(code_blocks))

def extract_code_blocks(gpt4_output):
    """
    Extract code blocks from the GPT-4 output.
    """
    print("Extracting code blocks from GPT-4 output")
    code_blocks = []
    lines = gpt4_output.split("\n")
    in_code_block = False
    current_code_block = ""
    for line in lines:
        if line.startswith(CODE_BLOCK_START) or line.startswith(CODE_BLOCK_START_PYTHON):
            in_code_block = True
        elif line.startswith(CODE_BLOCK_END):
            in_code_block = False
            code_blocks.append(current_code_block)
            current_code_block = ""
        elif in_code_block:
            current_code_block += line + "\n"
    return code_blocks

if __name__ == "__main__":
    configuration.initialize_config()
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".prompt"):
                file_path = os.path.join(root, file)
                if change_detection.detect_changes(file_path, file_path + ".checksum"):
                    process_file(file_path)
                    change_detection.set_unchanged(file_path, file_path + ".checksum")