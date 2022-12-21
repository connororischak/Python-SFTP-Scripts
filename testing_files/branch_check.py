import os
import subprocess
import time

ticketNo = 49470

os.system('cd /Users/ConnorO/pdoc_repos/peopledoc-sftp-accounts/host_vars/atl.ucloud.int/eeyore-0.atl.ucloud.int/customers')

checkBranch = subprocess.run(['git', 'ls-remote', '--exit-code', 'origin', f'INT-{ticketNo}'], stdout=subprocess.DEVNULL)
print(checkBranch.returncode)
if (checkBranch.returncode != '2'):
	branchExists = True
	print(f'Found branch INT-{ticketNo}, aborting....')
	if branchExists: quit()
else:
	print('No existing branch found!')
