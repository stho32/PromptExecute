import os
import hashlib
import argparse
from library.configuration import initialize_config, get_gpt4_key
from library.chatgpt import call_gpt_4

def create_checksum(file_path):
    """
    Create a checksum for a file.
    """
    with open(file_path, 'rb') as file:
        data = file.read()
        return hashlib.md5(data).hexdigest()

def process_file(file_path):
    """
    Process a .prompt file.
    """
    print(f"Processing file: {file_path}")
    output_file_name = None
    prepared_prompt = ""
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if line.startswith('#include'):
            include_file_path = os.path.join(os.path.dirname(file_path), line[8:].strip())
            with open(include_file_path, 'r') as include_file:
                prepared_prompt += include_file.read() + "\n"
        elif line.startswith('#write-to'):
            output_file_name = os.path.join(os.path.dirname(file_path), line[10:].strip())
        else:
            prepared_prompt += line
    with open(file_path + '.completed', 'w') as file:
        file.write(prepared_prompt)
    gpt4_key = get_gpt4_key()
    gpt4_output = call_gpt_4(gpt4_key, prepared_prompt)
    with open(file_path + '.output', 'w') as file:
        file.write(gpt4_output)
    if output_file_name:
        post_process(output_file_name, gpt4_output)

def post_process(output_file_name, gpt4_output):
    """
    Post-process the output from GPT-4.
    """
    print(f"Post-processing output to: {output_file_name}")
    code_blocks = gpt4_output.split('```')[1::2]
    with open(output_file_name, 'w') as file:
        file.write("\n".join(code_blocks))

def main(file_path):
    """
    Main function to walk through a directory structure.
    """
    initialize_config()
    if file_path.endswith('.prompt'):
        checksum_file_path = file_path + '.checksum'
        new_checksum = create_checksum(file_path)
        if os.path.exists(checksum_file_path):
            with open(checksum_file_path, 'r') as file:
                old_checksum = file.read().strip()
            if old_checksum != new_checksum:
                process_file(file_path)
                with open(checksum_file_path, 'w') as file:
                    file.write(new_checksum)
        else:
            process_file(file_path)
            with open(checksum_file_path, 'w') as file:
                file.write(new_checksum)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process .prompt files.')
    parser.add_argument('directory', nargs='?', default=os.getcwd())
    args = parser.parse_args()
    main(args.directory)