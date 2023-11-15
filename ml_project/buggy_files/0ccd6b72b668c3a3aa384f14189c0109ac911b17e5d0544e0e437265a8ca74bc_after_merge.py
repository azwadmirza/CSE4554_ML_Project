def get_preferred_submodules():
    """
    Get all submodules of the main scientific modules and others of our
    interest
    """
    # Path to the modules database
    modules_path = get_conf_path('db')

    # Modules database
    modules_db = PickleShareDB(modules_path)

    if 'submodules' in modules_db:
        return modules_db['submodules']

    submodules = []

    for m in PREFERRED_MODULES:
        submods = get_submodules(m)
        submodules += submods
    
    modules_db['submodules'] = submodules
    return submodules