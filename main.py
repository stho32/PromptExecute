import os
import hashlib
from library import configuration, chatgpt

def calculate_checksum(file_path):
    """
    Calculates the MD5 checksum of a file.
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

def process_file(file_path):
    """
    Processes a .prompt file, preparing the prompt, sending it to chat-GPT4, and handling the output.
    """
    print(f"Processing file: {file_path}")
    prepared_prompt = []
    output_file_name = None

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('#include'):
                include_file_path = os.path.join(os.path.dirname(file_path), line[8:].strip())
                with open(include_file_path, 'r') as include_file:
                    prepared_prompt.append(include_file.read())
            elif line.startswith('#write-to'):
                output_file_name = os.path.join(os.path.dirname(file_path), line[9:].strip())
            else:
                prepared_prompt.append(line)

    prepared_prompt_str = '\n'.join(prepared_prompt)
    with open(file_path + '.completed', 'w') as completed_file:
        completed_file.write(prepared_prompt_str)

    print("Sending prompt to chat-GPT4...")
    gpt4_key = configuration.get_gpt4_key()
    gpt4_output = chatgpt.call_gpt_4(gpt4_key, prepared_prompt_str)

    with open(file_path + '.output', 'w') as output_file:
        output_file.write(gpt4_output)

    if output_file_name:
        post_process_output(output_file_name, gpt4_output)

def post_process_output(output_file_name, gpt4_output):
    """
    Post-processes the output of chat-GPT4, extracting code blocks and writing them to a file.
    """
    print(f"Post-processing output to: {output_file_name}")
    code_blocks = gpt4_output.split('```')[1::2]
    with open(output_file_name, 'w') as output_file:
        output_file.write('\n'.join(code_blocks))

def main(directory):
    """
    Walks through a directory structure, looking for .prompt files and processing them.
    """
    print(f"Starting in directory: {directory}")
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.prompt'):
                file_path = os.path.join(root, file)
                checksum_file_path = file_path + '.checksum'
                current_checksum = calculate_checksum(file_path)

                if os.path.exists(checksum_file_path):
                    with open(checksum_file_path, 'r') as checksum_file:
                        previous_checksum = checksum_file.read().strip()
                else:
                    previous_checksum = None

                if current_checksum != previous_checksum:
                    with open(checksum_file_path, 'w') as checksum_file:
                        checksum_file.write(current_checksum)
                    process_file(file_path)

if __name__ == "__main__":
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    configuration.initialize_config()
    main(directory)