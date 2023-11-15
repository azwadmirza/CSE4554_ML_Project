def install_prerequisites():
	# pre-requisites for bench repo cloning
	run_os_command({
		'apt-get': [
			'sudo apt-get update',
			'sudo apt-get install -y git build-essential python3-setuptools python3-dev libffi-dev'
		],
		'yum': [
			'sudo yum groupinstall -y "Development tools"',
			'sudo yum install -y epel-release redhat-lsb-core git python-setuptools python-devel openssl-devel libffi-devel'
		]
	})

	install_package('curl')
	install_package('wget')
	install_package('git')
	install_package('pip3', 'python3-pip')

	success = run_os_command({
		'python3': "sudo -H python3 -m pip install --upgrade setuptools cryptography ansible==2.8.5 pip"
	})

	if not (success or shutil.which('ansible')):
		could_not_install('Ansible')