# Prerequisites:

# 1. if you don't have pip:
#   - brew install pip

# 2. Install virtualenv
#   - pip install virtualenv

# 3. Create Virtual Env for python scripting:
#   - virualenv PythonVenv (this will create a folder called PythonVenv (with the venv installed) inside your working directory)
#   - source bin/activate or source PythonVenv/bin/activate

# 4. Install the JIRA library
#   - pip install jira

# 5. To launch the application:
#   - python create_new_sftp.py

# 6. (optional) 
# If you want to also use Jira Shell:
#   - pip install keyring
#   - pip install IPython
# Launch with
#   - jirashell -s https://people-doc.atlassian.net -u [your-jira-email] -p [your-api-token]
import datetime
import sys
from jira import JIRA

jiraOptions = {'server': "https://people-doc.atlassian.net"}

jira = JIRA(options = jiraOptions, basic_auth = ('','')) # ('your jira email','your jira api key')

global sftp_username
sftp_username = ''
global pc_env
pc_env = ''
global subType
subType = ''
global ymlPath
ymlPath = ''
global issue
global ticketNo
global runMode



isIssue = False
while not isIssue:
    ticketNo = input("Ticket Number? ")
    try:
        issue = jira.issue(f'INT-{ticketNo}')
        isIssue = True
    except:
        print('Issue not found')
if issue.fields.issuetype.name != 'SFTP':
    print('Not an SFTP Ticket. Closing.')
    quit()
thing = issue.fields.customfield_11107[0].value
if thing != 'Creation':
    print('Not an SFTP Creation Ticket. ')
    quit()

runMode = ''
while runMode not in ('l', 't', 'L','T'):
    runMode = input('Live or Test? [L/T]: ')
if runMode.upper() == 'T':
    print(f'You are in TEST Mode.')
if runMode.upper() == 'L':
    print(f'WARNING: You are in LIVE Mode.\nPlease make sure you are on the correct branch by using:\n\tgit checkout -b INT-{ticketNo}\n')



def test():
    global ymlPath
    ymlPath = '' # put a file path here where you'd like yml's placed locally for test mode.
    print(f'\n[TESTING MODE] YML filepath: {ymlPath}')


def getInfo():
    global issue
    global sftp_username
    global pc_env
    sftp_username = issue.fields.customfield_10976
    pc_env = issue.fields.customfield_11130.value
    print(f'Username: {sftp_username}')
    print(f'People Care Environment: {pc_env}')


def makeFile():
    global issue
    titles = issue.fields.summary.split(' - ')
    if titles[0] != 'ACN': 
        customer = titles[1]
    else:
        customer = titles[2]
    jdate = issue.fields.created
    dates = jdate.split('T')
    dt = datetime.datetime.strptime(dates[0],"%Y-%m-%d")
    today = f"{dt.month}-{dt.day}-{dt.year}"
    key = str(issue.fields.customfield_11084).split('\n\n')
    yml = open(f'{ymlPath}{sftp_username}.yml','x')
    yml.write(f'{sftp_username}:\n')
    yml.write('  account_type: customer\n')
    yml.write(f'  sftp_user: {sftp_username}\n')
    yml.write(f'  sftp_group: {sftp_username}\n')
    yml.write(f'  sftp_customer_full_name: "{customer}"\n')
    yml.write(f'  sftp_date_creation: "{today}"\n')
    yml.write(f'  sftp_pub_keys_ukg:\n')
    yml.write(f'  - key: "{key[0]}"\n    ticket_date: "{today}"\n    ticket_ref: "https://people-doc.atlassian.net/browse/INT-{ticketNo}"\n')
    print(f'\n\t{sftp_username}.yml created at {ymlPath}')


def printCommit():
    global issue
    global ticketNo
    print()
    print('Commit message contents:\n')
    print(issue.fields.summary)
    print(f'https://people-doc.atlassian.net/browse/INT-{ticketNo}')
    if pc_env == 'prod-atl': 
        print(f'time ansible-playbook sftp_account.yml -l P-ATL-sftp-0 -t account -e "filter_names={sftp_username}"')
    elif pc_env == 'prod-tor':
        print(f'time ansible-playbook sftp_account.yml -l P-TOR-sftp-0 -t account -e "filter_names={sftp_username}"')
    elif pc_env == 'prod-eu':
        print(f'time ansible-playbook sftp_account.yml -l P-EU-eeyore-0 -t account -e "filter_names={sftp_username}"')
    elif pc_env == 'prod-us':
        print(f'time ansible-playbook sftp_account.yml -l P-US-eeyore -t account -e "filter_names={sftp_username}"') 
    elif pc_env == 'staging-us':
        print(f'time ansible-playbook sftp_account.yml -l S-US-eeyore -t account -e "filter_names={sftp_username}"')
    elif pc_env == 'staging-eu':
        print(f'time ansible-playbook sftp_account.yml -l S-EU-eeyore -t account -e "filter_names={sftp_username}"')
    print()


# replace the paths below with the paths to your local repo's
def mapEnv():
    global pc_env
    global ymlPath
    if pc_env == 'prod-atl': 
        ymlPath = '/Users/ConnorO/pdoc_repos/peopledoc-sftp-accounts/host_vars/atl.ucloud.int/eeyore-0.atl.ucloud.int/customers/'
    elif pc_env == 'prod-tor':
        ymlPath = '/Users/ConnorO/pdoc_repos/peopledoc-sftp-accounts/host_vars/tor.ucloud.int/eeyore-0.tor.ucloud.int/customers/'
    elif pc_env == 'prod-eu':
        ymlPath = '/Users/ConnorO/pdoc_repos/peopledoc-sftp-accounts/host_vars/de.people-doc.net/eeyore-0.de.people-doc.net/customers/ '
    elif pc_env == 'prod-us':
        ymlPath = '/Users/ConnorO/pdoc_repos/peopledoc-sftp-accounts/host_vars/us.people-doc.net/eeyore-000.us.people-doc.net/customers/'
    elif pc_env == 'staging-us':
        ymlPath = '/Users/ConnorO/pdoc_repos/peopledoc-sftp-accounts/host_vars/staging.us.people-doc.net/staging-depot-0.staging.us.people-doc.net/customers/'
    elif pc_env == 'staging-eu':
        ymlPath = '/Users/ConnorO/pdoc_repos/peopledoc-sftp-accounts/host_vars/staging.eu.people-doc.net/staging-depot-0.staging.eu.people-doc.net/customers/'
    print(f'\n[LIVE MODE] YML filepath: {ymlPath}')


def confirm():
    global ticketNo
    resp = ''
    while resp not in ('Y','N'):
        resp = input(f'Have you branched? [y/n] ')
        resp = resp.upper()
    if resp == 'Y':
        return True
    if resp == 'N':
        print(f'Please branch using git checkout -b INT-{ticketNo} and restart the script.')
        quit()


if runMode.upper() == 'L':
    checkedOut = confirm()
getInfo()
# run test() to test script, will NOT put file in Git repo
if runMode.upper() == 'T':
    test()
# run mapEnv() when doing live run. WILL put file in Git repo
if runMode.upper() == 'L':
    if checkedOut:
        mapEnv()
makeFile()
printCommit()