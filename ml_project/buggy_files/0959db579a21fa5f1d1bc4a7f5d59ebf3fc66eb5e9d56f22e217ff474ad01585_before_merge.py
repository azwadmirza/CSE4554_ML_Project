def is_64bit_windows_os():
    '''
    Checks for 64 bit Windows OS using environment variables.
    :return:
    '''
    return 'PROGRAMFILES(X86)' in os.environ