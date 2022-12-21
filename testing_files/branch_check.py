import os
import subprocess
import time

ticketNo = 12345

checkBranch = subprocess.run(['git', 'ls-remote', '--exit-code', 'origin', f'INT-{ticketNo}'], stdout=subprocess.DEVNULL)
print(checkBranch.returncode)
if (checkBranch.returncode != 2):
	branchExists = True
	print(f'Found branch INT-{ticketNo}, aborting....')
	if branchExists: quit()
else:
	print('No existing branch found!')
