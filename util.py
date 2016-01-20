import re
import sqlite3
import json
import requests
from requests.adapters import HTTPAdapter

NOT_DEPOSITED = 'not-deposited'
SUBMITTED = 'submitted'

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=10))

connection = sqlite3.connect('ctns.db')
cursor = connection.cursor()

registries = json.load(open("./registries.json"))

def extract_ctn(text):
  matches = []
  text = text.lower()
  for registry in registries:

    doi = registry['doi']
    re_relaxed = registry["regular-expression-relaxed"]
    re_cleanup_from = registry["regular-expression-cleanup"][0]
    re_cleanup_to = registry["regular-expression-cleanup"][1]
    re_strict = registry["regular-expression-strict"]

    # Collect any CTNs that match the regular expression exactly.
    strict_matches = re.findall(re_strict, text)
    matches.extend([(match, doi) for match in strict_matches])

    # Any that match the relaxed regex, apply the cleanup regex
    # then check for strict regex before adding.
    relaxed_matches = re.findall(re_relaxed, text)
    for match in relaxed_matches:
      tidied = re.sub(re_cleanup_from, re_cleanup_to, match)
  
      if re.match("^" + re_strict + "$", tidied):
        matches.append((tidied, doi))

  return set(matches)
