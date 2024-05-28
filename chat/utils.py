import os
import textwrap
import pygments
import google.generativeai as genai

import markdown


def run_llm(chat_history, context):
    # Or use `` to fetch an environment variable.
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "get_one_from_google")

    genai.configure(api_key=GOOGLE_API_KEY)
    models = ["gemini-1.5-flash-latest", 'gemini-1.5-pro']
    model = genai.GenerativeModel(models[0], system_instruction=context)

    # TODO: need to check if the chat history is too long and make it shorter
    messages = [*chat_history]
    token_count = model.count_tokens(messages)

    # check the number of tokens
    # if too big, new message = [history (minus first message)] (keep checking until under a milly)
    # in the future we want to mark some messages as no delete

    response = model.generate_content(
        messages,
        safety_settings={
            'HATE': 'BLOCK_NONE',
            'HARASSMENT': 'BLOCK_NONE',
            'SEXUAL': 'BLOCK_NONE',
            'DANGEROUS': 'BLOCK_NONE'
        }
    )

    return response.text


def to_markdown(text):
  text = text.replace('•', '  *')
  wrapped = textwrap.indent(text, '> ', predicate=lambda _: True)
  html = markdown.markdown(wrapped, extensions=['pymdownx.superfences', 'codehilite', 'pymdownx.highlight', 'pymdownx.magiclink', 'pymdownx.emoji', 'pymdownx.details', 'tables'])
  return html


def count_tokens(messages):

    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "get_one_from_google")

    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-pro')
    token_count = model.count_tokens(messages)
    token_count = token_count.total_tokens
    print(token_count)

    return token_count
