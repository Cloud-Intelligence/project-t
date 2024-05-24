import algoliasearch_django as algoliasearch
from .models import Chat

algoliasearch.register(Chat)
