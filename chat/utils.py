import os
import textwrap
import pygments
import google.generativeai as genai

import markdown


def run_llm(chat_history, context):
    # Or use `` to fetch an environment variable.
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "get_one_from_google")

    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-1.5-pro')
    context_message = {"role": "user", "parts": [context]}

    messages = [context_message, *chat_history]

    # check the number of tokens
    # if too big, new message = context + [history (minus first message)] (keep checking until under a milly)
    # in the future we want to mark some messages as no delete

    response = model.generate_content(messages)
    token_count = model.count_tokens(messages)
    print(token_count)

    return response.text


def to_markdown(text):
  text = text.replace('•', '  *')
  wrapped = textwrap.indent(text, '> ', predicate=lambda _: True)
  print(wrapped)
  html = markdown.markdown(wrapped, extensions=['pymdownx.superfences', 'codehilite', 'pymdownx.highlight', 'pymdownx.magiclink', 'pymdownx.emoji', 'pymdownx.details', 'tables'])
  print(html)
  return html


def count_tokens(messages):

    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "get_one_from_google")

    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-pro')
    token_count = model.count_tokens(messages)
    token_count = token_count.total_tokens
    print(token_count)

    return token_count
