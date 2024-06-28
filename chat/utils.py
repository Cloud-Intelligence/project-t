import os
import textwrap
import pygments
import google.generativeai as genai

import markdown

from chat.models import Message

MAX_TOKENS = 128000  # Maximum number of tokens allowed


def run_llm(chat_history, context):
    # Or use `` to fetch an environment variable.
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "get_one_from_google")

    genai.configure(api_key=GOOGLE_API_KEY)
    models = ["gemini-1.5-flash-latest", 'gemini-1.5-pro']
    model = genai.GenerativeModel(models[0], system_instruction=context)

    messages = [
        {"role": msg["role"], "parts": msg["parts"], "pk": msg.get("pk"), "starred": msg.get("starred", False),
         "tokens": msg["tokens"]}
        for msg in chat_history
    ]

    permanent_messages = [msg for msg in messages if msg['starred']]
    deletable_messages = [msg for msg in messages if not msg['starred']]

    total_tokens = sum(msg["tokens"] for msg in messages)

    while total_tokens > MAX_TOKENS:
        if deletable_messages:
            total_tokens -= deletable_messages.pop(0)["tokens"]  # Remove the oldest deletable message from the history

    messages = permanent_messages + deletable_messages

    response = model.generate_content(
        messages,
        safety_settings={
            'HATE': 'BLOCK_NONE',
            'HARASSMENT': 'BLOCK_NONE',
            'SEXUAL': 'BLOCK_NONE',
            'DANGEROUS': 'BLOCK_NONE'
        }
    )

    return response.text, response.count_tokens.total_tokens


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
