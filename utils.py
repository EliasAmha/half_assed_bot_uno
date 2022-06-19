from dataclasses import dataclass
import re, requests
import logging

@dataclass
class Phrase:
  title: str
  quote: str
  url: str

def get_csrf_token(n=10):
  logging.debug("[get_csrf_token](n=%d)", n)
  HOME_URL = "https://www.playphrase.me"
  csrf_regex = r'var csrfToken = "(.*?)";'
  logging.info("Initializing CSRF token generator...")
  while True:
    logging.info("Requesting home page...")
    r = requests.get(HOME_URL)
    logging.info("Got response from home page. response.status_code=%d", r.status_code)
    csrf_token = re.search(csrf_regex, r.text).group(1)
    logging.info("Got CSRF token: %s", csrf_token)
    cookies = r.cookies
    logging.info("Got cookies: %s", cookies)
    for _ in range(n):
      logging.info("Yielding csrf_token and cookies. csrf_token=%s, cookies=%s", csrf_token, cookies)
      yield csrf_token, cookies

CSRF_TOKEN_GENERATOR = get_csrf_token()

def get_results(query=""):
  logging.debug("[get_results](query=%s)", query)
  API_URL = "https://www.playphrase.me/api/v1/phrases/search?q=" + query + "&limit=10&platform=desktop%20safari&skip=0"
  logging.info("Initializing API request...")
  csrf_token, cookies = next(CSRF_TOKEN_GENERATOR)
  logging.info("Got csrf_token and cookies. csrf_token=%s, cookies=%s", csrf_token, cookies)
  headers = {
    'Accept': 'json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Authorization': 'Token',
    'Connection': 'keep-alive',
    'Content-Type': 'json',
    'Referer': 'https://www.playphrase.me/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36',
    'X-Csrf-Token': "cmf6ALYjeK3Xxi1Wobc1dIitdPqz+IjROylUqKHePZ+HQCkfROzIedaKmgSWlbgJogBBpd5HpkcmvFLF",
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
  }
  logging.debug("Headers: %s", headers)
  r = requests.get(API_URL, headers=headers, cookies=cookies)
  logging.info("Got response from API. response.status_code=%d", r.status_code)
  if not r.status_code == 200:
    logging.error("Error: Expected response code 200 but got %d", r.status_code)
    logging.error("Error: %s", r.text)
    return 0, []

  count = r.json().get("count", 0)
  phrases_data = r.json().get("phrases", [])
  phrases = [
    Phrase(title=phrase_data.get('video-info').get('info'), url=phrase_data.get('video-url'), quote=phrase_data.get('text')) for phrase_data in phrases_data
  ]

  return count, phrases