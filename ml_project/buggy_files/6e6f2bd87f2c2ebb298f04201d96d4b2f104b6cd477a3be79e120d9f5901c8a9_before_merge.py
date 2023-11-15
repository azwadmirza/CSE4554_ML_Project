def is_smartos_globalzone():
    '''
    Function to return if host is SmartOS (Illumos) global zone or not
    '''
    if not is_smartos():
        return False
    else:
        cmd = ['zonename']
        try:
            zonename = subprocess.Popen(
                cmd, shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            return False
        if zonename.returncode:
            return False
        if zonename.stdout.read().strip() == 'global':
            return True

        return False