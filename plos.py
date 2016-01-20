from util import extract_ctn, session, connection, cursor, insert_ctn, SUBMITTED, NOT_DEPOSITED
import xml.etree.ElementTree as ET

PAGE_SIZE = 40

def fetch_page(page_number):
  """Fetch a page from the PLOS API, extract CTNs and insert into the database."""
  params = {"q": "trial_registration:*",
            "fq": "doc_type:full",
            "fl": "id,title_display,trial_registration",
            "rows": PAGE_SIZE,
            "start": page_number * PAGE_SIZE}
  response = session.get("http://api.plos.org/search", params=params)
  
  tree = ET.fromstring(response.content)
  docs = tree.findall("result/doc")
  for doc in docs:
    work_doi = doc.find("str[@name='id']").text
    ctn_inputs = doc.find("arr[@name='trial_registration']").findall("str")
    
    if not work_doi.startswith("10."):
      continue

    for ctn_input in ctn_inputs:
      extracted_ctns = extract_ctn(ctn_input.text)

      for [ctn, registry_doi] in extracted_ctns:
        insert_ctn(ctn, registry_doi, work_doi)

def fetch_pages():
  """Iterate over all pages in the API and extract CTNs."""
  params = {"q": "trial_registration:*",
            "fq": "doc_type:full",
            "fl": "id,title_display,trial_registration"}

  response = session.get("http://api.plos.org/search", params=params)

  tree = ET.fromstring(response.content)
  num_found = int(tree.find("result").attrib['numFound'])

  last_page = num_found / PAGE_SIZE + 1

  for page in xrange(0, last_page + 1):
    print("Page {} of {}".format(page, last_page))
    fetch_page(page)
