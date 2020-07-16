import requests

API_ENDPOINT = 'https://api.quotable.io/random'

def get_quote():
  r = requests.get(API_ENDPOINT)
  response = r.json()
  return {
    'content': response['content'],
    'author': response['author']
  }
