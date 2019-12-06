#!/usr/bin/python3
import argparse
import datetime
import requests

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
parser.add_argument('-U', '--user', required=True,
                    help='check usage of this user')
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
start = parsed.start
end = parsed.end

output_header = 'Usage for USER {} [{}, {}]: '.format(user, start, end)
base_url = 'http://localhost:8880/mybrc-rest'

url_usages = base_url + '/user_project_usages'
request_params = {
    'user': user,
    'start_time': start,
    'end_time': end
}

usages = requests.get(url=url_usages,
                      params=request_params)
usages = usages.json()
responses = usages['results']

if len(responses) == 0:
    print(f'no projects by user {user}')
    exit(0)
else:
    print(output_header)

for response in responses:
    project = response['user_project']
    usage = response['usage']

    print(f'\tproject {project.project.name} usage is {usage}')
