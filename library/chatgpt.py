import openai

def call_gpt_4(openaikey, prompt):
    """
    Calls the GPT-4 model from the OpenAI API to process a given prompt.

    Parameters:
    - openaikey (str): The API key provided by OpenAI to authenticate requests.
    - prompt (str): The input text/message that you want GPT-4 to process.

    Returns:
    - str: The GPT-4 model's response to the given prompt.

    Notes:
    - This function sets the 'temperature' parameter to 0.5, which controls the randomness of the model's output.
      A lower value makes the output more deterministic, while a higher value makes it more random.
    - Ensure that the OpenAI library is properly installed and up-to-date in your environment.
    """

    openai.api_key = openaikey

    response = openai.ChatCompletion.create(
        model = "gpt-4",
        messages = [
            {'role': 'user', 'content': prompt}
        ],
        temperature = 0.2 
    )

    return response.choices[0]['message']['content'].strip()  # type: ignore
