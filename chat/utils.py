import os
import textwrap
import pygments
import google.generativeai as genai

import markdown
import psycopg2
from psycopg2.extras import RealDictCursor


def natural_language_to_sql(question, db_schema):
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "get_one_from_google")
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = f"""
    Given the following database schema:
    {db_schema}

    Convert the following natural language question into a SQL query:
    "{question}"

    Return only the SQL query, without any additional explanation.
    """

    response = model.generate_content(prompt)
    return response.text.strip()


def execute_sql_query(query):
    # Use your database connection parameters
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        results = cur.fetchall()

    conn.close()
    return results


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
