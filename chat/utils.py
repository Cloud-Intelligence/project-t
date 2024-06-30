import os
import textwrap
import pygments
import google.generativeai as genai
from google.cloud import storage
from vertexai.generative_models import GenerativeModel, Part
import vertexai
from .models import Message

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

def process_pdf(pdf_upload):
    project_id = os.getenv('PROJECT_ID')
    vertexai.init(project=project_id, location="us-central1")

    # Upload PDF to Google Cloud Storage
    storage_client = storage.Client()
    bucket_name = os.getenv('BUCKET_NAME')
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(f'pdfs/{pdf_upload.file.name}')
    blob.upload_from_filename(pdf_upload.file.path)

    pdf_uri = f'gs://{bucket_name}/pdfs/{pdf_upload.file.name}'

    model = GenerativeModel(model_name="gemini-1.5-pro-001")

    prompt = """
    You are a very professional document summarization specialist.
    Please summarize the given document.
    """
    
    pdf_file = Part.from_uri(pdf_uri, mime_type="application/pdf")
    contents = [pdf_file, prompt]

    response = model.generate_content(contents)
    return response.text if response.text else "Summary generation failed."