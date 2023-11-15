    def __init__(self, namelist=None, pathlist=None):
        if namelist is None:
            namelist = []
        spy_modules = ['sitecustomize', 'spyder', 'spyderplugins']
        mpl_modules = ['matplotlib', 'tkinter', 'Tkinter']
        # Add other, necessary modules to the UMR blacklist
        # astropy: see issue 6962
        # pytorch: see issue 7041
        other_modules = ['pytorch']
        if PY2:
            other_modules.append('astropy')
        self.namelist = namelist + spy_modules + mpl_modules + other_modules

        if pathlist is None:
            pathlist = []
        self.pathlist = pathlist
        self.previous_modules = list(sys.modules.keys())