# Prerequisites:

# Please create an environment variable by doing:
#   nano ~/.zprofile
#   add these lines to that file
#       export YML_BASE_PATH='[your home directory]' example /Users/[username]/
#       export JIRA_USER=[your jira login email]
#       export JIRA_KEY=[your jira API key]


# 1. if you don't have pip:
#   - brew install python (everyone should have python, pip is included with python)
#   - to see if you have pip:
#     pip --version

# 2. Install virtualenv
#   - pip install virtualenv

# 3. Create Virtual Env for python scripting:
#   - virualenv PythonVenv (this will create a folder called PythonVenv (with the venv installed) inside your working directory)
#   - source bin/activate or source PythonVenv/bin/activate

# 4. Install the JIRA library
#   - pip install jira

# 5. To launch the application:
#   - python helper_sftp.py

# 6. (optional) 
# If you want to also use Jira Shell:
#   - pip install keyring
#   - pip install IPython
# Launch with
#   - jirashell -s https://people-doc.atlassian.net -u [your-jira-email] -p [your-api-token]

import datetime
import os
from jira import JIRA

jiraOptions = {'server': "https://people-doc.atlassian.net"}

jira = JIRA(options = jiraOptions, basic_auth = (os.environ['JIRA_USER'],os.environ['JIRA_KEY']))

global data
data = []
global ticketNo
ticketNo = ''
global itemType
global issue
global numIP
global numcSSH
global numuSSH
global pc_env
global tags
tags = ''
pc_env = ''
global sftp_username
sftp_username = ''

def read():
    global issue
    isIssue = False
    while not isIssue:
        global ticketNo
        ticketNo = input("Ticket Number? ")
        try:
            issue = jira.issue(f'INT-{ticketNo}')
            isIssue = True
        except:
            print('Issue not found')
    global itemType
    itemType = input("IP, SSH, or all? ")
    global pc_env
    pc_env = issue.fields.customfield_11130.value
    global sftp_username
    sftp_username = issue.fields.customfield_10976
    global numIP
    numIP = 0
    global numcSSH
    numcSSH = 0
    global numuSSH
    numuSSH = 0
    if itemType == 'IP': 
        global data
        data = str(issue.fields.customfield_11082).split('\n')
        global tags
        tags = 'firewall'
    elif itemType == 'SSH':
        owner = input('Whose key? [c] for client, [u] for ukrewer [b] for both ')
        if owner == 'c':
            tags = 'ssh_customer'
            data = str(issue.fields.customfield_11083).split('\n\n')
        elif owner == 'u':
            tags = 'ssh_ukg'
            data = str(issue.fields.customfield_11084).split('\n\n')
        elif owner == 'b':
            tags = 'ssh_customer,ssh_ukg'
            items = str(issue.fields.customfield_11083).split('\n\n')
            for item in items: 
                if item != "None": 
                    data.append(item)
                    numcSSH += 1
            items = str(issue.fields.customfield_11084).split('\n\n')
            for item in items: 
                if item != "None":
                    data.append(item)
                    numuSSH += 1
    elif itemType == 'all':
        tags = 'firewall,ssh_customer,ssh_ukg'
        items = str(issue.fields.customfield_11082).split('\n')
        for item in items:
            if item != "None":
                data.append(item)
                numIP += 1
        items = str(issue.fields.customfield_11083).split('\n\n')
        for item in items: 
            if item != "None": 
                data.append(item)
                numcSSH += 1
        items = str(issue.fields.customfield_11084).split('\n\n')
        for item in items: 
            if item != "None":
                data.append(item)
                numuSSH += 1
    
    


def format(items):
    jdate = issue.fields.created
    dates = jdate.split('T')
    dt = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
    today = str(dt).split(' ')[0]
    entry = ''
    if itemType == 'all':
        if numIP != 0:
            print('  sftp_iptables:')
            for i in range (numIP):
                if i < numIP:
                    entry = '  - cidr: '
                    print(f'{entry}"{items[i]}"\n    ticket_date: "{today}"\n    ticket_ref: "https://people-doc.atlassian.net/browse/INT-{ticketNo}"')
        if numcSSH != 0:
            print('  sftp_pub_keys_clients:')
            for i in range (numcSSH):
                entry = '  - key: '
                print(f'{entry}"{items[i+numIP]}"\n    ticket_date: "{today}"\n    ticket_ref: "https://people-doc.atlassian.net/browse/INT-{ticketNo}"')
        if numuSSH != 0:
            print('  sftp_pub_keys_ukg:')
            for i in range (numuSSH):
                entry = '  - key: '
                print(f'{entry}"{items[i+numIP+numcSSH]}"\n    ticket_date: "{today}"\n    ticket_ref: "https://people-doc.atlassian.net/browse/INT-{ticketNo}"')
    elif itemType == 'IP':
        entry = '  - cidr: '
        for item in items:
            print(f'{entry}"{item}"\n    ticket_date: "{today}"\n    ticket_ref: "https://people-doc.atlassian.net/browse/INT-{ticketNo}"')
    elif itemType == 'SSH':
        entry = '  - key: '
        for item in items:
            print(f'{entry}"{item}"\n    ticket_date: "{today}"\n    ticket_ref: "https://people-doc.atlassian.net/browse/INT-{ticketNo}"')

def printCommit():
    global issue
    global ticketNo
    print()
    print('Commit message contents:\n')
    print(issue.fields.summary)
    print(f'https://people-doc.atlassian.net/browse/INT-{ticketNo}')
    if pc_env == 'prod-atl': 
        print(f'time ansible-playbook sftp_account.yml -l P-ATL-sftp-0 -t {tags} -e "filter_names={sftp_username}"')
    elif pc_env == 'prod-tor':
        print(f'time ansible-playbook sftp_account.yml -l P-TOR-sftp-0 -t {tags} -e "filter_names={sftp_username}"')
    elif pc_env == 'prod-eu':
        print(f'time ansible-playbook sftp_account.yml -l P-EU-eeyore-0 -t {tags} -e "filter_names={sftp_username}"')
    elif pc_env == 'prod-us':
        print(f'time ansible-playbook sftp_account.yml -l P-US-eeyore -t {tags} -e "filter_names={sftp_username}"') 
    elif pc_env == 'staging-us':
        print(f'time ansible-playbook sftp_account.yml -l S-US-eeyore -t {tags} -e "filter_names={sftp_username}"')
    elif pc_env == 'staging-eu':
        print(f'time ansible-playbook sftp_account.yml -l S-EU-eeyore -t {tags} -e "filter_names={sftp_username}"')
    print()

read()
format(data)
printCommit()
