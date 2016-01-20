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

def insert_ctn(ctn, registry_doi, work_doi):
  """Insert a CTN, registry  for a given DOI. May be called repeatedly, won't create duplicates."""
  
  if cursor.execute("select count(*) from ctns where ctn = ? and doi = ?", [ctn, work_doi]).fetchone()[0] == 0:
    cursor.execute("insert into ctns (ctn, registry, doi, status) values (?,?,?,?)", [ctn, registry_doi, work_doi, NOT_DEPOSITED])
    connection.commit()