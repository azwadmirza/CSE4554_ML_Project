def get_default_cwd():
    """Determine a reasonable default cwd"""
    try:
        cwd = os.getcwd()
    except (FileNotFoundError,OSError):
        err("unable to set current working directory, does not exist")
        cwd = '/'
    
    return(cwd)