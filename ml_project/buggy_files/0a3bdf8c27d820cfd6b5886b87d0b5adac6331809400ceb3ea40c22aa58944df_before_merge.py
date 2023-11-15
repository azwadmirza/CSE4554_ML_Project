def _get_msiexec(use_msiexec):
    '''
    Return if msiexec.exe will be used and the command to invoke it.
    '''
    if use_msiexec is False:
        return (False, '')
    if os.path.isfile(use_msiexec):
        return (True, use_msiexec)
    else:
        log.warning(("msiexec path '{0}' not found. Using system registered"
                     " msiexec instead").format(use_msiexec))
        use_msiexec = True
    if use_msiexec is True:
        return (True, 'msiexec')