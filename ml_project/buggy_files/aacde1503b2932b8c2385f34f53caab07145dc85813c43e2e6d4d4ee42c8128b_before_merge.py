def get_resource_path(filename):
    """
    Returns the absolute path of a resource, regardless of whether OnionShare is installed
    systemwide, and whether regardless of platform
    """
    p = get_platform()
    if p == 'Linux' and sys.argv and sys.argv[0].startswith(sys.prefix):
        # OnionShare is installed systemwide in Linux
        resources_dir = os.path.join(sys.prefix, 'share/onionshare')
    elif getattr(sys, 'frozen', False): # Check if app is "frozen" with cx_Freeze
        # http://cx-freeze.readthedocs.io/en/latest/faq.html#using-data-files
        resources_dir = os.path.join(os.path.dirname(sys.executable), 'resources')
    else:  # Look for resources directory relative to python file
        resources_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))), 'resources')

    return os.path.join(resources_dir, filename)