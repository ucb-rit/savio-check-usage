import argparse
import datetime

# import requests
import urllib2
import urllib

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
parser.add_argument('-A', '--account', required=True,
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
account = parsed.account
start = parsed.start
end = parsed.end

output_template = 'Usage for USER {} [{}, {}]: '.format(account, start, end)
output_template += '{} jobs, {} CPUHrs, {} SUs'


auth_token = '6905b2f4dc8798f5cff7c9af0fe93cab0dec193a'
auth_header = {'Authorization': 'Token {}'.format(auth_token)}
base_url = 'https://scgup-dev.lbl.gov:8443/mybrc-rest'

account_usages_params = {
    'account': account,
    'start_time': start,
    'end_time': end
}

url_account_usages = base_url + '/account_usages' + '?' \
    + urllib.urlencode(account_usages_params)

req_account_usages = urllib2.Request(url_account_usages, auth_header)

try:
    res_account_usages = urllib2.urlopen(req_account_usages)
    account_usages = res_account_usages.read()
except urllib2.URLError:
    raise SystemExit("ERROR: Failed to connect to backend...")

# account_usages = requests.get(url=url_account_usages,
#                               params=account_usages_params,
#                               headers=auth_header)

print('DEBUG: ', account_usages)
