def get_default_cwd():
    """Determine a reasonable default cwd"""
    cwd = os.getcwd()
    if not os.path.exists(cwd) or not os.path.isdir(cwd):
        try:
            cwd = pwd.getpwuid(os.getuid())[5]
        except KeyError:
            cwd = '/'
    
    return(cwd)