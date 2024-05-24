import os
import textwrap
import google.generativeai as genai

import markdown


def run_llm(chat_history, context):
    # Or use `` to fetch an environment variable.
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "get_one_from_google")

    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-pro')
    context_message = {"role": "user", "parts": [context]}
    messages = [context_message, *chat_history]

    response = model.generate_content(messages)
    print(response)

    return response.text


def to_markdown(text):
  text = text.replace('•', '  *')
  # text = text.replace('\n', '<br>')
  wrapped = textwrap.indent(text, '> ', predicate=lambda _: True)
  html = markdown.markdown(wrapped, extensions=['fenced_code', 'codehilite', 'tables'])
  print(html)
  return html
