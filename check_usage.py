#!/usr/bin/python
import argparse
import datetime

import urllib2
import urllib
import json

docstr = '''
This script shows account usage
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


base_url = 'https://scgup-dev.lbl.gov:8443/mybrc-rest'


request_params = {
    'account': account,
    'start_time': start,
    'end_time': end
}
account_usages_url = base_url + '/account_usages' + '?' + \
    urllib.urlencode(request_params)

try:
    account_usages = urllib2.urlopen(account_usages_url).read()
except urllib2.URLError, e:
    print 'ERROR: Failed to connect to API:', e.reason
    exit(0)


if account_usages is None:
    print 'INFO: No data received for given query...'
    exit(0)

account_usages = json.loads(account_usages)
print 'Usage for ACCOUNT %s [%s, %s]: %s' % account % start % end \
    % account_usages.usage
