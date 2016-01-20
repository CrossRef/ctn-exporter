# Clinical Trials Importer

A proof-of-concept utility to allow publishers to deposit CTNs (Clinical Trials Numbers) in bulk, for example, from text-mining. The initial release contains an adaptor for PLOS, but it can easily be extended to use any data source. This is only of use to publishers.

## Requirements

This is a Python program. It uses the Requests library: http://docs.python-requests.org/en/latest/user/install/#install

## To run

You will probably want to extend this in order for it to be useful to you.

### Import data

To import data, for example from the PLOS API:

    python main.py import-plos

This will find CTNs and idenitfy the registry they belong to. You can run this more than once without creating duplicates.

### Deposit with Crossref

You will need your Crossref username and password.

    python main.py deposit --username USERNAME --password PASSWORD

Depending on how many CTNs you have, this may take a while.

### Check status

To view the status of deposits:

    python main.py update --username USERNAME --password PASSWORD

Then

    python main.py status

You can run this every hour or so to check on the status of the deposits. Wait up to 24 hours before looking for your CTNs in the Crossref API.

## Extending

For this to be useful to you, you will need to write a script to get CTNs out of your data source, identify the CTN Registry, and put them into the database. See `plos.py` for an example. Please contact labs@crossref.org and we'll be happy to help you.


