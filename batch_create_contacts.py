#!/usr/bin/env python
"""
This script will batch create contacts (i.e. reverse-aliases)
for one of your simple-login.io aliases.

python batch_create_contacts.py <alias> <csv with a "contact" column with all the emails you want a reverse alias for>
"""
import argparse
import collections
import json
import os
import pathlib
import re
import pprint
from typing import Dict, List, Optional

from dotenv import load_dotenv
import pandas as pd
import requests

load_dotenv()


SIMPLELOGIN_BASE='https://app.simplelogin.io/api'
email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', re.IGNORECASE)

pp = pprint.PrettyPrinter(indent=2)


def endpoint_url(e:str) -> str:
    return f'{SIMPLELOGIN_BASE}/{e}'


def simplelogin(endpoint, method='GET', params = None, json = None):
    headers = {'Authentication': os.environ['SIMPLELOGIN_APIKEY']}
    return requests.request(
        method,
        endpoint_url(endpoint),
        headers=headers,
        params=params,
        json=json,
    )


def get_user_info():
    return simplelogin('user_info')


def is_valid_email(s: str) -> bool:
    return bool(email_pattern.match(s))


def get_aliases(page=0, aliases = []):
    response = simplelogin('v2/aliases', method = 'GET', params = {'page_id': page})
    paged_aliases = response.json()['aliases']
    if not paged_aliases: return aliases
    return get_aliases(page=page+1, aliases = aliases + paged_aliases)


def find_alias(aliases: List[str], email: str) -> Optional[Dict]:
    return next((a for a in aliases if a['email'] == email), None)


def create_contact(alias_id, contact) -> requests.models.Response:
    endpoint = f'aliases/{alias_id}/contacts'
    return simplelogin(endpoint, 'POST', json={'contact': contact})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='create reverse aliases for a simplelogin alias (put API_KEY on .env) and call this script with 2 string params (the alias you want to create reverse aliases for and a csv with a "contact" column that contains all of the emails you would like to create a reverse alias for')
    parser.add_argument('alias')
    parser.add_argument('emails_csv')
    args = parser.parse_args()

    u = get_user_info().json()
    a = get_aliases()

    if not is_valid_email(args.alias):
        raise ValueError(f'{args.alias} is not a valid email')

    alias = find_alias(a, args.alias)
    new_contacts = pd.read_csv(args.emails_csv).contact.tolist()

    for c in new_contacts:
        if not is_valid_email(c):
            raise ValueError(f'{c} in {args.emails_csv} is not a valid email')

    print('User and alias info to create contacts')
    pp.pprint(u)
    pp.pprint(alias)

    print('Creating contacts:', new_contacts)
    results = [create_contact(alias['id'], c) for c in new_contacts]

    # print the results
    sorted_results = collections.defaultdict(list)
    reverse_aliases = {}
    for r in results:
        contact = json.loads(r.request.body)['contact']
        sorted_results[r.status_code] = contact
        if r.status_code in (200, 201):
            reverse_aliases[contact] = r.json()['reverse_alias_address']
    pp.pprint(sorted_results)

    print('Here are your reverse aliases')
    pp.pprint(reverse_aliases)

    pathlib.Path('./tmp').mkdir(exist_ok=True)

    print('I\'ll also put them in this file: tmp/reverse_aliases.csv')
    reverse_aliases_df = pd.DataFrame.from_dict(reverse_aliases, orient='index').reset_index()
    reverse_aliases_df.columns = ['contact', 'alias']
    reverse_aliases_df.to_csv('tmp/reverse_aliases.csv', index=False)
