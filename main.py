import sqlite3
import json
import argparse
from xml.sax.saxutils import escape
import plos
from util import session, connection, cursor, SUBMITTED, NOT_DEPOSITED

template = open("deposit.xml").read()

def print_status():
  result = cursor.execute("select status, count(distinct(ctn)) from ctns group by status").fetchall()

  print("Number of CTNs per status:")
  for (status, count) in result:
    print("{}: {}".format(status, count))

def poll_deposits(username, password):
  for (token, ctn, doi, status) in cursor.execute("select token, ctn, doi, status from ctns where status = ?", [SUBMITTED]):
    response = session.get("https://api.crossref.org/deposits/{}".format(token), auth=(username, password))
    
    if response.status_code == 401:
      print("Bad username and password")
      exit()

    new_status = response.json()['message']['status']

    print("Update {} in {} status {} -> {}".format(ctn, doi, status, new_status))  
    cursor.execute("update ctns set status = ? where token = ?", [status, token])
    connection.commit()
  
def send_deposits(username, password):
  to_deposit = cursor.execute("select ctn, doi, registry from ctns where status = ?", [NOT_DEPOSITED])

  for (ctn, doi, registry) in to_deposit:
    print("Deposit {} in {}".format(ctn, doi))
    templated = template.format(doi=escape(doi), registry=escape(registry), ctn=escape(ctn))

    response = session.post("https://api.crossref.org/deposits", data=templated, auth=(username, password), headers={"Content-Type": "application/vnd.crossref.partial+xml"})

    if response.status_code != 200:
      print("Error depositing: {}".format(response.status_code))
      print(response.text)
    else:
      token = response.json()['message']['batch-id']
      status = response.json()['message']['status']
      cursor.execute("update ctns set token = ?, status = ? where ctn = ? and doi = ?", [token, status, ctn, doi])
      connection.commit()
      print("Status of {} in {}: {}".format(ctn, doi, status))

try:
  curs = connection.execute("select * from ctns limit 0")
except sqlite3.OperationalError:
  cursor.execute("create table ctns (ctn text, registry text, doi text, status text, token text);")

parser = argparse.ArgumentParser(description='Collect and deposit Clinical Trial Numbers')
parser.add_argument('action', choices=['import-plos', 'deposit', 'update', 'status'])

parser.add_argument('--username', help='Crossref Username')
parser.add_argument('--password', help='Crossref Password')

args = parser.parse_args()

if args.action == 'import-plos':
  plos.fetch_pages()

elif args.action == 'deposit':
  send_deposits(args.username, args.password)

elif args.action == 'update':
  poll_deposits(args.username, args.password)

elif args.action == 'status':
  print_status()
