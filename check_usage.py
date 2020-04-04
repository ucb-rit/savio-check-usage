#!/usr/bin/python
import argparse
import datetime
import time

import urllib2
import urllib
import json

docstr = '''
This script shows user/project usage
'''

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
        raise argparse.ArgumentTypeError('Not a valid date: {}'.format(s))
    else:
        return s

def process_date_time(date_time):
    try:
        return time.mktime(time.strptime(date_time, timestamp_format_complete))
    except ValueError:
        return time.mktime(time.strptime(date_time, timestamp_format_minimal))



##### parse arguments #####



parser = argparse.ArgumentParser(description=docstr)

parser.add_argument('-U', '--user',
                                help='check usage of this user')
parser.add_argument('-A', '--account',
                                help='check usage of this account')

parser.add_argument('-s', '--start', type=valid_date,
                    help='start time YYYY-MM-DD[THH:MM:SS]'
                    '(DEFAULT: {}-06-01T00:00:00)'.format(datetime.datetime
                                                          .now().year),
                    default='{}-06-01T00:00:00'.format(datetime.datetime
                                                       .now().year))
parser.add_argument('-e', '--end', type=valid_date,
                    help='end time YYYY-MM-DD[THH:MM:SS]'
                    '(DEFAULT: Current TimeStamp)',
                    default=datetime.datetime.now()
                    .strftime(timestamp_format_complete))
parsed = parser.parse_args()
user = parsed.user
account = parsed.account
_start = parsed.start
_end = parsed.end
start = process_date_time(_start)
end = process_date_time(_end)

if not (user or account):
    parser.error('Atleast one of -U/--user and -A/--account required.')



##### prepare params #####



# base_url = 'https://scgup-dev.lbl.gov:8443/mybrc-rest'
base_url = 'http://localhost:8880/mybrc-rest'
request_urls = {}
output_headers = {}

if user:
    output_header = 'Usage for USER {} [{}, {}]: '.format(user, _start, _end)
    request_params = {
        'start_time': start,
        'end_time': end,
        'user': user
    }
    url_usages = base_url + '/user_account_usages?' + \
        urllib.urlencode(request_params)

    request_urls['user'] = url_usages
    output_headers['user'] = output_header

if account:
    output_header = 'Usage for ACCOUNT {} [{}, {}]: '.format(account, _start, _end)
    request_params = {
        'start_time': start,
        'end_time': end,
        'account': account
    }
    url_usages = base_url + '/account_usages?' + \
        urllib.urlencode(request_params)

    request_urls['account'] = url_usages
    output_headers['account'] = output_header

if user and account:
    output_header = 'Usage for USER:ACCOUNT {}:{} [{}, {}]: '.format(user, account, _start ,_end)
    request_params = {
        'start_time': start,
        'end_time': end,
        'user': user,
        'account': account
    }
    url_usages = base_url + '/user_account_usages?' + \
        urllib.urlencode(request_params)

    request_urls['user_account'] = url_usages
    output_headers['user_account'] = output_header



##### output functions #####



def get_allocation_for_account(account):
    request_params = {'name': account}
    req_url = base_url + '/projects?' + \
        urllib.urlencode(request_params)

    try:
        req = urllib2.Request(req_url)
        req.add_header("Authorization",
                        "Token cd36d6e6b80e4c292c8349f671a9d7814c977daa")
        response = json.loads(urllib2.urlopen(req).read())
        response = response['results']

    except urllib2.URLError:
        pass

    if len(response) != 0:
        return response[0]['allocation'] # best match


def process_user_account_usages(req_url):
    req = urllib2.Request(req_url)
    req.add_header("Authorization",
                    "Token cd36d6e6b80e4c292c8349f671a9d7814c977daa")
    response = json.loads(urllib2.urlopen(req).read())
    response = response['results']

    if len(response) == 0:
        print 'No such projects (', account, ') of user:', user
        return

    print output_headers['user_account']
    for single in response:
        user_account = single['user_account']
        usage = single['usage']

        print '\taccount', user_account['account'], 'usage by', user, 'is', usage, 'out of user allocation of', user_account['allocation']


def process_account_usages(req_url):
    req = urllib2.Request(req_url)
    req.add_header("Authorization",
                    "Token cd36d6e6b80e4c292c8349f671a9d7814c977daa")
    response = json.loads(urllib2.urlopen(req).read())
    response = response['results']

    if len(response) == 0:
        print 'No such user have tracked usages:', account
        return

    print output_headers['account']
    for single in response:
        usage = single['usage']
        account_project = single['account']
        account_allocation = get_allocation_for_account(account)

        print '\taccount',  account_project, 'total usage is', usage, 'out of project allocation of', account_allocation

    print


def process_user_usages():
    req = urllib2.Request(req_url)
    req.add_header("Authorization",
                    "Token cd36d6e6b80e4c292c8349f671a9d7814c977daa")
    response = json.loads(urllib2.urlopen(req).read())
    response = response['results']

    if len(response) == 0:
        print 'No such accounts have tracked usages:', user
        return

    print output_headers['user']
    for single in response:
        usage = single['usage']
        user_account = single['user_account']

        print '\taccount', user_account['account'], 'usage by', user, 'is', usage, 'out of user allocation of', user_account['allocation']

    print



##### get data #####



for req_type, req_url in request_urls.items():
    try:
        if req_type == 'user':
            process_user_usages()

        if req_type == 'user_account':
            process_user_account_usages(req_url)

        if req_type == 'account':
            process_account_usages(req_url)

    except urllib2.URLError, e:
        print (e.reason)
        pass # url error

    except ValueError, e:
        pass # json decode error

