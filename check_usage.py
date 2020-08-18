#!/usr/bin/python
import argparse
import datetime
import time
import getpass
import calendar

import urllib2
import urllib
import json


VERSION = 1.1
docstr = '''
[version: {}]
'''.format(VERSION)


BASE_URL = 'http://mybrc.brc.berkeley.edu/mybrc-rest/'
# BASE_URL = 'https://scgup-dev.lbl.gov:8443/mybrc-rest'
# BASE_URL = 'http://localhost:8880/mybrc-rest'

timestamp_format_complete = '%Y-%m-%dT%H:%M:%S'
timestamp_format_minimal = '%Y-%m-%d'


def red_str(vector):
    return "\033[91m {}\033[00m".format(vector)


def green_str(vector):
    return "\033[92m {}\033[00m".format(vector)


def yellow_str(vector):
    return "\033[93m {}\033[00m".format(vector)


def check_valid_date(s):
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


def to_timestamp(date_time):
    try:
        return calendar.timegm(time.strptime(date_time, timestamp_format_complete))
    except ValueError:
        return calendar.timegm(time.strptime(date_time, timestamp_format_minimal))


def get_account_start(account, user=None):
    request_params = {
        'account': account
    }

    if user:
        request_params['user'] = user
        url_transactions = BASE_URL + '/user_account_transactions?' + \
            urllib.urlencode(request_params)
    else:
        url_transactions = BASE_URL + '/account_transactions?' + \
            urllib.urlencode(request_params)

    try:
        req = urllib2.Request(url_transactions)
        response = json.loads(urllib2.urlopen(req).read())['results']
        target_start_date = response[0]['date_time']
    except urllib2.URLError:
        return None
    except KeyError:
        return None
    except IndexError:
        return None

    return target_start_date.split('.')[0] if '.' in target_start_date else target_start_date


current_month = datetime.datetime.now().month
current_year = datetime.datetime.now().year
default_start = current_year if current_month >= 6 else (current_year - 1)

parser = argparse.ArgumentParser(description=docstr)

parser.add_argument('-u', dest='user',
                    help='check usage of this user')
parser.add_argument('-a', dest='account',
                    help='check usage of this account')

parser.add_argument('-E', dest='expand', action='store_true',
                    help='expand user/account usage')
parser.add_argument('-s', dest='start', type=check_valid_date,
                    help='starttime for the query period (YYYY-MM-DD[THH:MM:SS])',
                    default='{}-06-01T00:00:00'.format(default_start))
parser.add_argument('-e', dest='end', type=check_valid_date,
                    help='endtime for the query period (YYYY-MM-DD[THH:MM:SS])',
                    default=datetime.datetime.now()
                    .strftime(timestamp_format_complete))
parsed = parser.parse_args()
user = parsed.user
account = parsed.account
expand = parsed.expand
_start = parsed.start
_end = parsed.end
start = to_timestamp(_start)
end = to_timestamp(_end)

default_start_used = _start == '{}-06-01T00:00:00'.format(default_start)
calculate_account_start_hide_allocation = default_start_used and account and not user
calculate_user_account_start = default_start_used and account and user

# just account information, calculate single start date
if calculate_account_start_hide_allocation:
    target_start_date = get_account_start(account)
    if target_start_date is not None:
        _start = target_start_date
        start = to_timestamp(_start)

# both account and user query, calculate single start date
if calculate_user_account_start:
    target_start_date = get_account_start(account, user)
    if target_start_date is not None:
        _start = target_start_date
        start = to_timestamp(_start)


if not user and not account:
    user = getpass.getuser()

request_urls = {}
output_headers = {}
if user:
    output_header = 'Usage for USER {} [{}, {}]:'.format(user, _start, _end)
    output_headers['user'] = output_header

if account:
    output_header = 'Usage for ACCOUNT {} [{}, {}]:'.format(
        account, _start, _end)
    output_headers['account'] = output_header


def url_get_user_usages(start, end, user, page=1):
    request_params = {
        'start_time': start,
        'end_time': end,
        'user': user,
        'page': page
    }
    url_usages = BASE_URL + '/user_account_usages?' + \
        urllib.urlencode(request_params)
    return url_usages


def url_get_zero_users(user, page=1):
    request_params = {
        'user': user,
        'page': page
    }
    url_usages = BASE_URL + '/user_accounts?' + \
        urllib.urlencode(request_params)
    return url_usages


def url_get_account_usages(start, end, account, page=1):
    request_params = {
        'start_time': start,
        'end_time': end,
        'account': account,
        'page': page
    }
    url_usages = BASE_URL + '/account_usages?' + \
        urllib.urlencode(request_params)
    return url_usages


def url_get_zero_accounts(account, page=1):
    request_params = {
        'name': account,
        'page': page
    }
    url_usages = BASE_URL + '/accounts?' + \
        urllib.urlencode(request_params)
    return url_usages


def url_get_account_users(start, end, account, page=1):
    request_params = {
        'start_time': start,
        'end_time': end,
        'account': account,
        'page': page
    }
    url_usages = BASE_URL + '/user_account_usages?' + \
        urllib.urlencode(request_params)
    return url_usages


def url_get_zero_users(user, page=1):
    request_params = {
        'user': user,
        'page': page
    }
    url_usages = BASE_URL + '/user_accounts?' + \
        urllib.urlencode(request_params)
    return url_usages


def url_get_user_accounts(account, page=1):
    request_params = {
        'account': account,
        'page': page
    }
    url_usages = BASE_URL + '/user_accounts?' + \
        urllib.urlencode(request_params)
    return url_usages


def get_cpu_usage(user=None, account=None):
    request_params = {'start_time': start, 'end_time': end}
    if user:
        request_params['user'] = user

    if account:
        request_params['account'] = account

    req_url = BASE_URL + '/jobs?' + \
        urllib.urlencode(request_params)

    try:
        req = urllib2.Request(req_url)
        response = json.loads(urllib2.urlopen(req).read())
    except urllib2.URLError:
        response = {'count': 0, 'total_cpu_time': 0, 'response': [], 'next': None}

    job_count = response['count']
    cpu_time = response['total_cpu_time']

    return job_count, cpu_time


def get_cpu_usage_old(user=None, account=None, page=1):
    request_params = {'page': page, 'start_time': start, 'end_time': end}
    if user:
        request_params['user'] = user

    if account:
        request_params['account'] = account

    req_url = BASE_URL + '/jobs?' + \
        urllib.urlencode(request_params)

    try:
        req = urllib2.Request(req_url)
        response = json.loads(urllib2.urlopen(req).read())
    except urllib2.URLError:
        response = {'next': None, 'response': []}

    if response['next']:
        later_job_count, later_cpu_time = get_cpu_usage(user, account, page + 1)
    else:
        later_job_count, later_cpu_time = 0, 0.0

    net_cpu_time = 0.0
    jobs = response['results']
    for job in jobs:
        net_cpu_time += job['cpu_time'] if job['cpu_time'] else 0.0

    return len(jobs) + later_job_count, net_cpu_time + later_cpu_time


def get_account_allocation(account):
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


def paginate_requests(url_function, params):
    req = urllib2.Request(url_function(*params))
    response = json.loads(urllib2.urlopen(req).read())

    table = response['results']
    page = 2
    while response['next'] is not None:
        try:
            req = urllib2.Request(url_function(*params, page=page))
            response = json.loads(urllib2.urlopen(req).read())
            table.extend(response['results'])
            page += 1
        except urllib2.URLError:
            response['next'] = None

    return table


def process_account_query():
    response = paginate_requests(url_get_account_usages, [start, end, account])
    response = response if len(response) != 0 else paginate_requests(url_get_zero_accounts, [account])

    if len(response) == 0:
        print 'ERROR: Account', account, 'not defined.'
        return

    single = response[0]
    if 'usage' not in single:
        usage = 0
        account_project = single['name']
        account_allocation = single['allocation']
        job_count, account_cpu = 0, 0.0
    else:
        usage = single['usage']
        account_project = single['account']
        account_allocation = get_account_allocation(account)
        job_count, account_cpu = get_cpu_usage(account=account)

    account_allocation = int(float(account_allocation))

    # if time specified: no allocation
    if not default_start_used:  # user specified time range
        print output_headers['account'], job_count, 'jobs,', '{:.2f}'.format(account_cpu), 'CPUHrs,', usage, 'SUs.'
    else:
        print output_headers['account'], job_count, 'jobs,', '{:.2f}'.format(account_cpu), 'CPUHrs,', usage, 'SUs used from an allocation of', account_allocation, 'SUs.'

    if expand:
        responses = paginate_requests(
            url_get_account_users, [start, end, account])

        user_dict = {}
        for single in responses:
            user_dict[single['user_account']['user']] = True
            percentage = 0.0
            try:
                percentage = (float(single['usage']) / float(usage)) * 100
            except ValueError:
                pass
            except ZeroDivisionError:
                percentage = 0.00

            user_jobs, user_cpu = get_cpu_usage(single['user_account']['user'],
                                                single['user_account']['account'])

            if percentage < 75:
                color_fn = green_str
            elif percentage > 100:
                color_fn = red_str
            else:
                color_fn = yellow_str

            percentage = color_fn("{:.2f}".format(percentage))

            print '\tUsage for USER {} in ACCOUNT {} [{}, {}]: {} jobs,' \
                ' {:.2f} CPUHrs, {} ({}%) SUs.' \
                .format(single['user_account']['user'],
                        single['user_account']['account'],
                        _start, _end, user_jobs, user_cpu, single['usage'],
                        percentage)

        user_list = paginate_requests(url_get_user_accounts, [account])
        for single in user_list:
            if single['user'] in user_dict or single['user'] is None:
                continue

            percentage = 0.0
            user_jobs, user_cpu = 0, 0
            color_fn = green_str
            percentage = color_fn("{:.2f}".format(percentage))

            print '\tUsage for USER {} in ACCOUNT {} [{}, {}]: {} jobs,' \
                ' {:.2f} CPUHrs, {} ({}%) SUs.' \
                .format(single['user'],
                        single['account'],
                        _start, _end, user_jobs, user_cpu, 0,
                        percentage)


def process_user_query():
    zero_user = False
    response = paginate_requests(url_get_user_usages, [start, end, user])

    if len(response) == 0:
        response = paginate_requests(url_get_zero_users, [user])
        zero_user = True

    if len(response) == 0:
        print 'ERROR: User', user, 'not defined.'
        return

    usage = 0.0
    extended = []
    if not zero_user:
        for single in response:
            try:
                usage += float(single['usage'])
                extended.append(single)
            except ValueError:
                pass

    job_count, user_cpu = get_cpu_usage(user=user)
    print output_headers['user'], job_count, 'jobs,', '{:.2f}'.format(user_cpu), 'CPUHrs,', usage, 'SUs used.'

    if expand and len(extended) != 0:
        for single in extended:
            user_jobs, user_cpu = get_cpu_usage(single['user_account']['user'],
                                                single['user_account']['account'])

            print '\tUsage for USER {} in ACCOUNT {} [{}, {}]: {} jobs,'\
                ' {:.2f} CPUHrs, {} SUs.' \
                .format(single['user_account']['user'],
                        single['user_account']['account'],
                        _start, _end, user_jobs, user_cpu, single['usage'])


for req_type in output_headers.keys():
    try:
        if start > end:
            print 'ERROR: Start time ({}) requested is after end time ({}).'.format(_start, _end)
            exit(0)

        if to_timestamp('2020-06-01') > start:
            print 'INFO: Information might be inaccurate, for accurate information contact BRC support (brc-hpc-help@berkeley.edu).'

        if req_type == 'user':
            process_user_query()

        if req_type == 'account':
            if account.startswith('ac_'):
                print 'INFO: Start Date shown may be inaccurate.'

            process_account_query()

    except urllib2.URLError, e:
        # print(e.reason)
        print('Error: Could not connect to backend, contact BRC Support (brc-hpc-help@berkeley.edu) if problem persists.')
        pass  # url error

    except ValueError, e:
        pass  # json decode error
