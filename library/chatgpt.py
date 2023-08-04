import openai

def call_gpt_4(openaikey, prompt):
    openai.api_key = openaikey

    response = openai.ChatCompletion.create(
        model = "gpt-4",
        messages = [
            {'role': 'user', 'content': prompt}
        ],
        temperature = 0.5 
    )

    return response.choices[0]['message']['content'].strip()  # type: ignore