def transfer_file(module, dest):
    file_size = os.path.getsize(module.params['local_file'])

    if not enough_space(module):
        module.fail_json(msg='Could not transfer file. Not enough space on device.')

    provider = module.params['provider']

    hostname = module.params.get('host') or provider.get('host')
    username = module.params.get('username') or provider.get('username')
    password = module.params.get('password') or provider.get('password')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=hostname,
        username=username,
        password=password)

    full_remote_path = '{}{}'.format(module.params['file_system'], dest)
    scp = SCPClient(ssh.get_transport())
    try:
        scp.put(module.params['local_file'], full_remote_path)
    except:
        time.sleep(10)
        temp_size = verify_remote_file_exists(
            module, dest, file_system=module.params['file_system'])
        if int(temp_size) == int(file_size):
            pass
        else:
            module.fail_json(msg='Could not transfer file. There was an error '
                             'during transfer. Please make sure remote '
                             'permissions are set.', temp_size=temp_size,
                             file_size=file_size)
    scp.close()
    ssh.close()
    return True