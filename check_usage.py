#!/usr/bin/python
import argparse
import datetime

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


parser = argparse.ArgumentParser(description=docstr)

user_account_group = parser.add_mutually_exclusive_group(required=True)
user_account_group.add_argument('-U', '--user',
                                help='check usage of this user')
user_account_group.add_argument('-A', '--account',
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
start = parsed.start
end = parsed.end


base_url = 'https://scgup-dev.lbl.gov:8443/mybrc-rest'

request_params = {
    'start_time': start,
    'end_time': end
}

if user and not account:
    output_header = 'Usage for USER {} [{}, {}]: '.format(user, start, end)
    request_params['user'] = user
    url_usages = base_url + '/user_account_usages?' + \
        urllib.urlencode(request_params)

elif account and not user:
    output_header = 'Usage for ACCOUNT {} [{}, {}]: '.format(account, start, end)
    request_params['account'] = account
    url_usages = base_url + '/account_usages?' + \
        urllib.urlencode(request_params)
else:
    output_header = 'Usage for USER:ACCOUNT {}:{} [{}, {}]: '.format(user,
                                                                     account,
                                                                     start,
                                                                     end)
    request_params['account'] = account
    request_params['user'] = user
    url_usages = base_url + '/user_account_usages?' + \
        urllib.urlencode(request_params)

try:
    req_account_usages = urllib2.Request(url_usages)
    res_account_usages = urllib2.urlopen(req_account_usages)
    usages = res_account_usages.read()
except urllib2.URLError:
    raise SystemExit("ERROR: Failed to connect to backend...")

if usages.status_code != 200:
    raise SystemExit("ERROR: Request to backend failed...")

usages = usages.json()
responses = usages['results']

if len(responses) == 0:
    print 'No projects by user', user
    exit(0)
else:
    print output_header

for response in responses:
    project = response['user_project']
    usage = response['usage']

    print '\tproject', project.project.name, ' usage is', usage

