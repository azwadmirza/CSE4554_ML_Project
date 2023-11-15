def is_smartos_globalzone():
    '''
    Function to return if host is SmartOS (Illumos) global zone or not
    '''
    if not is_smartos():
        return False
    else:
        try:
            zonename_proc = subprocess.Popen(
                ['zonename'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
            zonename_output = zonename_proc.communicate()[0].strip().decode(__salt_system_encoding__)
            zonename_retcode = zonename_proc.poll()
        except OSError:
            return False
        if zonename_retcode:
            return False
        if zonename_output == 'global':
            return True

        return False