def get_preferred_submodules():
    """
    Get all submodules of the main scientific modules and others of our
    interest
    """
    if 'submodules' in modules_db:
        return modules_db['submodules']
    
    mods = ['numpy', 'scipy', 'sympy', 'pandas', 'networkx', 'statsmodels',
            'matplotlib', 'sklearn', 'skimage', 'mpmath', 'os', 'PIL',
            'OpenGL', 'array', 'audioop', 'binascii', 'cPickle', 'cStringIO',
            'cmath', 'collections', 'datetime', 'errno', 'exceptions', 'gc',
            'imageop', 'imp', 'itertools', 'marshal', 'math', 'mmap', 'msvcrt',
            'nt', 'operator', 'parser', 'rgbimg', 'signal', 'strop', 'sys',
            'thread', 'time', 'wx', 'xxsubtype', 'zipimport', 'zlib', 'nose',
            'PyQt4', 'PySide', 'os.path']

    submodules = []

    for m in mods:
        submods = get_submodules(m)
        submodules += submods
    
    modules_db['submodules'] = submodules
    return submodules