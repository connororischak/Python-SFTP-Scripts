import os
import subprocess
import time



checkBranch = subprocess.run(['git', 'checkout', '-b', f'branch2'], stdout=subprocess.DEVNULL)
print(f'Checkout returned with exit code: {checkBranch.returncode}')
if (checkBranch.returncode == 0):
	branchExists = False
	print(f'Branched successfully!')
	subprocess.run(['git', 'checkout', 'testing_exit_code'])
	subprocess.run(['git', 'branch', '--delete', 'branch2'])
else:
	print('Could not branch. Branch already exists. aborting....')
	quit()
		
