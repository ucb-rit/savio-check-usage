#!/usr/bin/python
import argparse
import datetime
import time
import getpass

import urllib2
import urllib
import json


VERSION = 0.1
docstr = '''
[version: {}]
'''.format(VERSION)

##### params #####

# BASE_URL = 'http://mybrc.brc.berkeley.edu/mybrc-rest/'
# BASE_URL = 'https://scgup-dev.lbl.gov:8443/mybrc-rest'
BASE_URL = 'http://localhost:8880/mybrc-rest'

timestamp_format_complete = '%Y-%m-%dT%H:%M:%S'
timestamp_format_minimal = '%Y-%m-%d'


def valid_date(s):
    '''check if date is in valid format(s)'''
    complete, minimal = None, None

    try:
        complete = datetime.datetime.strptime(s, timestamp_format_complete)
    except ValueError:
        pass

    try:
        minimal = datetime.datetime.strptime(s, timestamp_format_minimal)
    except ValueError:
        pass

    if not complete and not minimal:  # doesn't fit either format
        raise argparse.ArgumentTypeError(
            'Invalid time specification {}'.format(s))
    else:
        return s


def process_date_time(date_time):
    try:
        return time.mktime(time.strptime(date_time, timestamp_format_complete))
    except ValueError:
        return time.mktime(time.strptime(date_time, timestamp_format_minimal))


##### parse arguments #####


current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year
default_start = current_year if current_month >= 6 else (current_year - 1)
parser = argparse.ArgumentParser(description=docstr)

parser.add_argument('-u', dest='user',
                    help='check usage of this user')
parser.add_argument('-a', dest='account',
                    help='check usage of this account')

parser.add_argument('-s', dest='start', type=valid_date,
                    help='starttime for the query period (YYYY-MM-DD[THH:MM:SS])',
                    default='{}-06-01T00:00:00'.format(default_start))
parser.add_argument('-e', dest='end', type=valid_date,
                    help='endtime for the query period (YYYY-MM-DD[THH:MM:SS])',
                    default=datetime.datetime.now()
                    .strftime(timestamp_format_complete))
parsed = parser.parse_args()
user = parsed.user
account = parsed.account
_start = parsed.start
_end = parsed.end
start = process_date_time(_start)
end = process_date_time(_end)

if not user and not account:
    user = getpass.getuser()


##### prepare params #####


request_urls = {}
output_headers = {}

if user:
    output_header = 'Usage for USER {} [{}, {}]: '.format(user, _start, _end)
    request_params = {
        'start_time': start,
        'end_time': end,
        'user': user
    }
    url_usages = BASE_URL + '/user_account_usages?' + \
        urllib.urlencode(request_params)

    request_urls['user'] = url_usages
    output_headers['user'] = output_header

if account:
    output_header = 'Usage for ACCOUNT {} [{}, {}]:'.format(
        account, _start, _end)
    request_params = {
        'start_time': start,
        'end_time': end,
        'account': account
    }
    url_usages = BASE_URL + '/account_usages?' + \
        urllib.urlencode(request_params)

    request_urls['account'] = url_usages
    output_headers['account'] = output_header


##### output functions #####


def get_allocation_for_account(account):
    request_params = {'name': account}
    req_url = BASE_URL + '/accounts?' + \
        urllib.urlencode(request_params)

    try:
        req = urllib2.Request(req_url)
        response = json.loads(urllib2.urlopen(req).read())
        response = response['results']

    except urllib2.URLError:
        response = []

    if len(response) != 0:
        return response[0]['allocation']  # best match


def process_account_usages(req_url):
    req = urllib2.Request(req_url)
    response = json.loads(urllib2.urlopen(req).read())
    response = response['results']

    if len(response) == 0:
        print 'ERROR: Account', account, 'not defined.'
        return

    single = response[0]
    usage = single['usage']
    account_project = single['account']
    account_allocation = get_allocation_for_account(account)
    print output_headers['account'], usage, 'SUs used from an allocation of', account_allocation, 'SUs.'


def process_user_usages():
    req = urllib2.Request(req_url)
    response = json.loads(urllib2.urlopen(req).read())
    response = response['results']

    if len(response) == 0:
        print 'ERROR: User', user, 'not defined.'
        return

    usage = 0.0
    for single in response:
        try:
            usage += float(single['usage'])
        except ValueError:
            pass

    print output_headers['user'], usage, 'SUs used.'


##### get data #####


for req_type, req_url in request_urls.items():
    try:
        if req_type == 'user':
            process_user_usages()

        if req_type == 'account':
            process_account_usages(req_url)

    except urllib2.URLError, e:
        print(e.reason)
        pass  # url error

    except ValueError, e:
        pass  # json decode error
